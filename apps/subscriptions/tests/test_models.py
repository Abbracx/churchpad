import pytest
from apps.subscriptions.models import Plan, Subscriber

@pytest.mark.django_db
def test_plan_creation():
    plan = Plan.objects.create(
        name="Premium Plan",
        stripe_price_id="price_12345",
        price=20.00,
        billing_period="month",
    )
    assert plan.name == "Premium Plan"
    assert plan.stripe_price_id == "price_12345"
    assert plan.price == 20.00
    assert plan.billing_period == "month"

@pytest.mark.django_db
def test_subscriber_creation():
    plan = Plan.objects.create(
        name="Basic Plan",
        stripe_price_id="price_67890",
        price=10.00,
        billing_period="month",
    )
    subscriber = Subscriber.objects.create(
        name="John Doe",
        email="john@example.com",
        phone_number="+15551234567",
        plan=plan,
        stripe_customer_id="cus_12345",
        stripe_subscription_id="sub_12345",
        is_active=True,
    )
    assert subscriber.name == "John Doe"
    assert subscriber.email == "john@example.com"
    assert subscriber.phone_number == "+15551234567"
    assert subscriber.plan == plan
    assert subscriber.stripe_customer_id == "cus_12345"
    assert subscriber.stripe_subscription_id == "sub_12345"
    assert subscriber.is_active is True