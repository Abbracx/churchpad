from django.urls import reverse
from rest_framework.test import APITestCase
from django.test import TestCase
from unittest.mock import patch
from .models import Subscriber, Plan
from django.conf import settings


class SubscriptionTests(APITestCase):
    def setUp(self):
        self.plan = Plan.objects.create(
            name="Basic Plan",
            stripe_price_id="price_test123",
            price=10.00,
            billing_period="month",
        )

    @patch("stripe.Customer.create")
    @patch("stripe.Subscription.create")
    @patch("subscriptions.tasks.send_welcome_sms.delay")
    def test_subscribe_success(self, mock_sms, mock_subscription, mock_customer):
        mock_customer.return_value.id = "cus_test123"
        mock_subscription.return_value.id = "sub_test123"
        data = {
            "name": "John Doe",
            "email": "john@example.com",
            "phone_number": "+15551234567",
            "plan_id": self.plan.id,
        }
        response = self.client.post(reverse("subscribe"), data)
        self.assertEqual(response.status_code, 201)
        self.assertTrue(Subscriber.objects.filter(email="john@example.com").exists())
        mock_sms.assert_called_once()

    def test_list_subscriptions(self):
        Subscriber.objects.create(
            name="Jane Doe",
            email="jane@example.com",
            phone_number="+15551234568",
            plan=self.plan,
            stripe_customer_id="cus_test456",
            stripe_subscription_id="sub_test456",
        )
        response = self.client.get(reverse("subscriptions"))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 1)

    def test_unsubscribe(self):
        subscriber = Subscriber.objects.create(
            name="Jane Doe",
            email="jane@example.com",
            phone_number="+15551234568",
            plan=self.plan,
            stripe_customer_id="cus_test456",
            stripe_subscription_id="sub_test456",
            is_active=True,
        )
        response = self.client.delete(reverse("unsubscribe", args=[subscriber.id]))
        self.assertEqual(response.status_code, 204)
        subscriber.refresh_from_db()
        self.assertFalse(subscriber.is_active)
