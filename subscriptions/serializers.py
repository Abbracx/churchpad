from rest_framework import serializers
from .models import Subscriber, Plan
import uuid

class PlanSerializer(serializers.ModelSerializer):
    class Meta:
        model = Plan
        fields = ['id', 'name', 'price', 'billing_period']

class ReadSubscriberSerializer(serializers.ModelSerializer):
    plan = PlanSerializer(read_only=True)
    # plan_id = serializers.IntegerField(write_only=True)

    class Meta:
        model = Subscriber
        fields = ['id', 'name', 'email', 'phone_number', 'plan', 'is_active', 'created_at']


class WriteSubscriberSerializer(serializers.ModelSerializer):
    # plan = PlanSerializer(read_only=True)
    plan_id = serializers.UUIDField(default=uuid.uuid4)

    class Meta:
        model = Subscriber
        fields = ['id', 'name', 'email', 'phone_number', 'plan_id',]



class RegisterPriceSerializer(serializers.ModelSerializer):
    name = serializers.CharField(max_length=100, required=True)
    currency = serializers.CharField(max_length=10, required=True)
    unit_amount = serializers.IntegerField(required=True, help_text="Unit amount in cents (e.g., 1000 for $10)")
    interval = serializers.ChoiceField(choices=['month', 'year'], required=True, help_text="Billing interval (e.g., 'month', 'year')")

    class Meta:
        model = Plan
        fields = ['name', 'currency', 'unit_amount', 'interval']