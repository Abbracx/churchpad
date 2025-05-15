import pytest
from django.urls import reverse
from apps.subscriptions.models import Plan, Subscriber
from unittest.mock import patch

@pytest.mark.django_db
def test_list_plans(client):
    Plan.objects.create(
        name="Basic Plan",
        stripe_price_id="price_12345",
        price=10.00,
        billing_period="month",
    )
    response = client.get(reverse("subscriptions:list_plans"))
    assert response.status_code == 200
    assert len(response.data) == 1
    assert response.data[0]["name"] == "Basic Plan"

@pytest.mark.django_db
@patch("apps.subscriptions.tasks.send_welcome_sms.delay")
@patch("apps.subscriptions.tasks.send_email_task.delay")
@patch("apps.subscriptions.services.StripeService.create_subscription")
@patch("apps.subscriptions.services.StripeService.create_customer")
def test_confirm_subscription(
    mock_create_customer, mock_create_subscription, mock_send_email, mock_send_sms, client
):
    plan = Plan.objects.create(
        name="Basic Plan",
        stripe_price_id="price_12345",
        price=10.00,
        billing_period="month",
    )
    mock_create_customer.return_value = {"id": "cus_12345"}
    mock_create_subscription.return_value = {"id": "sub_12345"}

    data = {
        "customer_id": "cus_12345",
        "plan_id": plan.id,
    }
    response = client.post(reverse("subscriptions:confirm_subscription"), data)
    assert response.status_code == 201
    assert Subscriber.objects.filter(stripe_customer_id="cus_12345").exists()
    mock_send_sms.assert_called_once()
    mock_send_email.assert_called_once()

@pytest.mark.django_db
def test_unsubscribe(client):
    plan = Plan.objects.create(
        name="Basic Plan",
        stripe_price_id="price_12345",
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
    response = client.delete(reverse("subscriptions:unsubscribe", args=[subscriber.id]))
    assert response.status_code == 204
    subscriber.refresh_from_db()
    assert subscriber.is_active is False

@pytest.mark.django_db
def test_list_subscriptions(client):
    plan = Plan.objects.create(
        name="Basic Plan",
        stripe_price_id="price_12345",
        price=10.00,
        billing_period="month",
    )
    Subscriber.objects.create(
        name="John Doe",
        email="john@example.com",
        phone_number="+15551234567",
        plan=plan,
        stripe_customer_id="cus_12345",
        stripe_subscription_id="sub_12345",
        is_active=True,
    )
    response = client.get(reverse("subscriptions:list_subscriptions"))
    assert response.status_code == 200
    assert len(response.data) == 1
    assert response.data[0]["name"] == "John Doe"