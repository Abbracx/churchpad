from django.db import transaction
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from .models import Subscriber, Plan
from .serializers import SubscriberSerializer
import stripe
from django.conf import settings
from .tasks import send_welcome_sms

stripe.api_key = settings.STRIPE_TEST_KEY

@api_view(['POST'])
def subscribe(request):
    serializer = SubscriberSerializer(data=request.data)
    if serializer.is_valid():
        try:
            plan = Plan.objects.get(id=serializer.validated_data['plan_id'])
        except Plan.DoesNotExist:
            return Response({'error': 'Invalid plan ID'}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            # Create Stripe Customer and Subscription
            customer = stripe.Customer.create(
                email=serializer.validated_data['email'],
                name=serializer.validated_data['name'],
                phone=serializer.validated_data['phone_number']
            )
            subscription = stripe.Subscription.create(
                customer=customer.id,
                items=[{'price': plan.stripe_price_id}],
            )
            
            # Create Subscriber within a transaction
            with transaction.atomic():
                subscriber = Subscriber.objects.create(
                    name=serializer.validated_data['name'],
                    email=serializer.validated_data['email'],
                    phone_number=serializer.validated_data['phone_number'],
                    plan=plan,
                    stripe_customer_id=customer.id,
                    stripe_subscription_id=subscription.id
                )
            
            # Trigger Celery task to send SMS
            send_welcome_sms.delay(subscriber.id)
            return Response(SubscriberSerializer(subscriber).data, status=status.HTTP_201_CREATED)
        
        except stripe.error.StripeError as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
def list_subscriptions(request):
    subscribers = Subscriber.objects.filter(is_active=True).select_related('plan')
    serializer = SubscriberSerializer(subscribers, many=True)
    return Response(serializer.data)

@api_view(['DELETE'])
def unsubscribe(request, id):
    try:
        subscriber = Subscriber.objects.get(id=id, is_active=True)
    except Subscriber.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)
    
    subscriber.is_active = False
    subscriber.save()
    return Response(status=status.HTTP_204_NO_CONTENT)

@api_view(['POST'])
def stripe_webhook(request):
    # Simulate handling Stripe webhook
    event_type = request.data.get('event_type')
    customer_id = request.data.get('customer_id')
    
    if event_type == 'payment_failed':
        try:
            subscriber = Subscriber.objects.get(stripe_customer_id=customer_id)
            subscriber.is_active = False
            subscriber.save()
            return Response({'status': 'subscription deactivated'})
        except Subscriber.DoesNotExist:
            return Response({'error': 'Subscriber not found'}, status=404)
    return Response({'status': 'ignored'})