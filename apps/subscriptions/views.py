
import logging
from django.db import transaction
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from .models import Subscriber, Plan
from .serializers import (
    PlanSerializer,
    ReadSubscriberSerializer,
    WriteSubscriberSerializer,
    RegisterPriceSerializer,
)
import stripe
from django.conf import settings
from .tasks import send_welcome_sms, send_email_task
from .services import StripeService


# Initialize logger
logger = logging.getLogger(__name__)


@swagger_auto_schema(
    method="post",
    operation_summary="Subscribe a user to a plan",
    operation_description="Creates a new subscription for a user by creating a Stripe customer, payment intent, and subscription, and saving the subscriber in the database.",
    request_body=WriteSubscriberSerializer,
    responses={
        201: ReadSubscriberSerializer,
        400: openapi.Response(description="Invalid input or Stripe error"),
    },
)
@api_view(["POST"])
def subscribe(request):
    logger.info("Processing subscription request")
    serializer = WriteSubscriberSerializer(data=request.data)
    if serializer.is_valid():
        try:
            plan = Plan.objects.get(id=serializer.validated_data["plan_id"])
            logger.info(f"Plan retrieved: {plan.name}")
        except Plan.DoesNotExist:
            logger.error("Invalid plan ID provided")
            return Response(
                {"error": "Invalid plan ID"}, status=status.HTTP_400_BAD_REQUEST
            )

        try:
            # Create Stripe Customer
            customer = StripeService.create_customer(
                email=serializer.validated_data["email"],
                name=serializer.validated_data["name"],
                phone_number=serializer.validated_data["phone_number"],
            )
            logger.info(f"Stripe customer created: {customer.id}")

            # Attach the PaymentMethod to the Customer
            payment_method_id = request.data.get("payment_method_id")
            if not payment_method_id:
                logger.error("Payment method ID is missing")
                return Response(
                    {"error": "Payment method ID is required"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            StripeService.attach_payment_method(payment_method_id, customer.id)
            logger.info(
                f"Payment method {payment_method_id} attached to customer {customer.id}"
            )

            # Create a PaymentIntent
            payment_intent = StripeService.create_payment_intent(
                amount=int(plan.price * 100),  # Convert price to cents
                currency="usd",
                customer_id=customer.id,
                metadata={"plan_id": plan.id},
            )
            logger.info(f"PaymentIntent created: {payment_intent.id}")

            # Return the PaymentIntent client secret to the frontend
            return Response(
                {
                    "client_secret": payment_intent.client_secret,
                    "customer_id": customer.id,
                    "plan_id": plan.id,
                },
                status=status.HTTP_201_CREATED,
            )

        except stripe.error.StripeError as e:
            logger.error(f"Stripe error: {str(e)}")
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
    else:
        logger.warning("Invalid subscription request data")
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# This view handles the confirmation of a subscription
@swagger_auto_schema(
    method="post",
    operation_summary="Confirm a subscription",
    operation_description="Confirms a subscription by creating a Stripe subscription for the customer and saving the subscriber in the database.",
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            "customer_id": openapi.Schema(
                type=openapi.TYPE_STRING, description="Stripe customer ID"
            ),
            "plan_id": openapi.Schema(
                type=openapi.TYPE_INTEGER, description="ID of the plan to subscribe to"
            ),
        },
        required=["customer_id", "plan_id"],
    ),
    responses={
        201: ReadSubscriberSerializer,
        400: openapi.Response(description="Invalid input or Stripe error"),
    },
)
@api_view(["POST"])
def confirm_subscription(request):
    logger.info("Processing subscription confirmation")
    customer_id = request.data.get("customer_id")
    plan_id = request.data.get("plan_id")

    try:
        plan = Plan.objects.get(id=plan_id)
        logger.info(f"Plan retrieved: {plan.name}")
        customer = stripe.Customer.retrieve(customer_id)
        logger.info(f"Stripe customer retrieved: {customer_id}")

        # Create a subscription
        subscription = StripeService.create_subscription(
            customer.id, plan.stripe_price_id
        )
        logger.info(f"Subscription created: {subscription.id}")

        # Save the subscriber in the database
        with transaction.atomic():
            subscriber = Subscriber.objects.create(
                name=customer.name,
                email=customer.email,
                phone_number=customer.phone,
                plan=plan,
                stripe_customer_id=customer.id,
                stripe_subscription_id=subscription.id,
            )
            logger.info(f"Subscriber saved: {subscriber.id}")

        # Trigger Celery task to send SMS
        send_welcome_sms.delay(subscriber.id)
        logger.info(f"Welcome SMS task triggered for subscriber {subscriber.id}")

        # Trigger Celery task to send email
        subject = "Welcome to ChurchPad"
        message = f"Hi {subscriber.name},\n\nThank you for subscribing to our service. We are excited to have you on board!"
        send_email_task.delay(subject, message, [subscriber.email])
        logger.info(f"Welcome email task triggered for subscriber {subscriber.id}")
        return Response(
            ReadSubscriberSerializer(subscriber).data, status=status.HTTP_201_CREATED
        )

    except Plan.DoesNotExist:
        logger.error("Invalid plan ID provided")
        return Response(
            {"error": "Invalid plan ID"}, status=status.HTTP_400_BAD_REQUEST
        )
    except stripe.error.StripeError as e:
        logger.error(f"Stripe error: {str(e)}")
        return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


# This view handles the listing of all active subscriptions
@swagger_auto_schema(
    method="get",
    operation_summary="List active subscriptions",
    operation_description="Retrieves a list of all active subscriptions, including their associated plans.",
    responses={
        200: ReadSubscriberSerializer(many=True),
    },
)
@api_view(["GET"])
def list_subscriptions(request):
    subscribers = Subscriber.objects.filter(is_active=True).select_related("plan")
    serializer = ReadSubscriberSerializer(subscribers, many=True)
    return Response(serializer.data)


# This view handles the unsubscription of a user
@swagger_auto_schema(
    method="delete",
    operation_summary="Unsubscribe a user",
    operation_description="Deactivates a subscription by setting the `is_active` field to `False`.",
    responses={
        204: openapi.Response(description="Subscription deactivated successfully"),
        404: openapi.Response(description="Subscriber not found"),
    },
)
@api_view(["DELETE"])
def unsubscribe(request, id):
    try:
        subscriber = Subscriber.objects.get(id=id, is_active=True)
    except Subscriber.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    subscriber.is_active = False
    subscriber.save()
    return Response(status=status.HTTP_204_NO_CONTENT)


# This view handles the listing of all available plans
@swagger_auto_schema(
    method="get",
    operation_summary="List all plans",
    operation_description="Retrieves a list of all available subscription plans.",
    responses={
        200: openapi.Response(
            description="List of plans", schema=ReadSubscriberSerializer(many=True)
        ),
    },
)
@api_view(["GET"])
def list_plans(request):
    plans = Plan.objects.all()
    serializer = PlanSerializer(plans, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)


# This view handles the registration of a price for a plan
@swagger_auto_schema(
    method="post",
    operation_summary="Register a price for a plan",
    operation_description="Creates a price for a plan using the Stripe Price API and stores the price in the database.",
    request_body=RegisterPriceSerializer,
    responses={
        201: openapi.Response(description="Price created and stored successfully"),
        400: openapi.Response(description="Invalid input or Stripe error"),
    },
)
@api_view(["POST"])
def register_price(request):
    logger.info("Processing price registration")
    serializer = RegisterPriceSerializer(data=request.data)
    if serializer.is_valid():
        data = serializer.validated_data
        try:
            # Create a price in Stripe
            price = StripeService.create_price(
                currency=data["currency"],
                unit_amount=data["unit_amount"],
                interval=data["interval"],
                product_name=data["name"],
            )
            logger.info(f"Stripe price created: {price.id}")

            # Save the price in the Plan model
            plan = Plan.objects.create(
                name=data["name"],
                stripe_price_id=price.id,
                price=data["unit_amount"] / 100,  # Convert cents to dollars
                billing_period=data["interval"],
            )
            logger.info(f"Plan saved: {plan.id}")

            # Return the created plan details
            return Response(
                {
                    "id": plan.id,
                    "name": plan.name,
                    "stripe_price_id": plan.stripe_price_id,
                    "price": plan.price,
                    "billing_period": plan.billing_period,
                },
                status=status.HTTP_201_CREATED,
            )

        except stripe.error.StripeError as e:
            logger.error(f"Stripe error: {str(e)}")
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
    else:
        logger.warning("Invalid price registration data")
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# This view handles Stripe webhook events
@swagger_auto_schema(
    method="post",
    operation_summary="Handle Stripe webhook events",
    operation_description="Handles Stripe webhook events such as `payment_failed`, `customer.subscription.created`, and others.",
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            "event_type": openapi.Schema(
                type=openapi.TYPE_STRING, description="Type of Stripe event"
            ),
            "customer_id": openapi.Schema(
                type=openapi.TYPE_STRING, description="Stripe customer ID"
            ),
        },
        required=["event_type", "customer_id"],
    ),
    responses={
        200: openapi.Response(description="Webhook processed successfully"),
        404: openapi.Response(description="Subscriber not found"),
    },
)
@api_view(["POST"])
def stripe_webhook(request):
    logger.info("Processing Stripe webhook")

    # Verify the payload
    try:
        payload = request.body
        sig_header = request.META.get("HTTP_STRIPE_SIGNATURE")
        event = stripe.Webhook.construct_event(
            payload, sig_header, settings.STRIPE_WEBHOOK_SECRET
        )
    except ValueError as e:
        logger.error("Invalid payload")
        return Response({"error": "Invalid payload"}, status=status.HTTP_400_BAD_REQUEST)
    except stripe.error.SignatureVerificationError as e:
        logger.error("Invalid signature")
        return Response({"error": "Invalid signature"}, status=status.HTTP_400_BAD_REQUEST)

    # Extract event type and customer ID
    event_type = event["type"]
    customer_id = event["data"]["object"].get("customer")

    if not event_type or not customer_id:
        logger.error("Missing event_type or customer_id in webhook payload")
        return Response(
            {"error": "Invalid payload"}, status=status.HTTP_400_BAD_REQUEST
        )

    try:
        subscriber = Subscriber.objects.get(stripe_customer_id=customer_id)
    except Subscriber.DoesNotExist:
        logger.error(f"Subscriber with customer_id {customer_id} not found")
        return Response(
            {"error": "Subscriber not found"}, status=status.HTTP_404_NOT_FOUND
        )

    # Handle different event types
    if event_type == "customer.subscription.created":
        logger.info(f"Handling customer.subscription.created for customer {customer_id}")
        subscriber.is_active = True
        subscriber.save()

        # Send email notification asynchronously
        subject = "Subscription Created"
        message = f"Dear {subscriber.name},\n\nYour subscription has been successfully created."
        send_email_task.delay(subject, message, [subscriber.email])

        return Response({"status": "subscription activated"})

    elif event_type == "customer.subscription.updated":
        logger.info(f"Handling customer.subscription.updated for customer {customer_id}")

        # Send email notification asynchronously
        subject = "Subscription Updated"
        message = f"Dear {subscriber.name},\n\nYour subscription has been updated."
        send_email_task.delay(subject, message, [subscriber.email])

        return Response({"status": "subscription updated"})

    elif event_type == "customer.subscription.deleted":
        logger.info(f"Handling customer.subscription.deleted for customer {customer_id}")
        subscriber.is_active = False
        subscriber.save()

        # Send email notification asynchronously
        subject = "Subscription Cancelled"
        message = f"Dear {subscriber.name},\n\nYour subscription has been cancelled."
        send_email_task.delay(subject, message, [subscriber.email])

        return Response({"status": "subscription deleted"})

    elif event_type == "payment_intent.succeeded":
        logger.info(f"Handling payment_intent.succeeded for customer {customer_id}")

        # Send email notification asynchronously
        subject = "Payment Successful"
        message = f"Dear {subscriber.name},\n\nYour payment was successful. Thank you!"
        send_email_task.delay(subject, message, [subscriber.email])

        return Response({"status": "payment succeeded"})

    else:
        logger.warning(f"Unhandled event type: {event_type}")
        return Response({"status": "event ignored"})