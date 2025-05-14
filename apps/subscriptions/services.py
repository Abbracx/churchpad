import stripe
from django.conf import settings

stripe.api_key = settings.STRIPE_TEST_KEY


class StripeService:
    @staticmethod
    def create_customer(email, name, phone_number):
        return stripe.Customer.create(email=email, name=name, phone=phone_number)

    @staticmethod
    def attach_payment_method(payment_method_id, customer_id):
        stripe.PaymentMethod.attach(
            payment_method_id,
            customer=customer_id,
        )
        stripe.Customer.modify(
            customer_id,
            invoice_settings={"default_payment_method": payment_method_id},
        )

    @staticmethod
    def create_payment_intent(amount, currency, customer_id, metadata):
        return stripe.PaymentIntent.create(
            amount=amount,
            currency=currency,
            customer=customer_id,
            setup_future_usage="off_session",
            metadata=metadata,
        )

    @staticmethod
    def create_subscription(customer_id, price_id):
        return stripe.Subscription.create(
            customer=customer_id,
            items=[{"price": price_id}],
        )

    @staticmethod
    def create_price(currency, unit_amount, interval, product_name):
        return stripe.Price.create(
            currency=currency,
            unit_amount=unit_amount,
            recurring={"interval": interval},
            product_data={"name": product_name},
        )
