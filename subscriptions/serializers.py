from rest_framework import serializers
from .models import Subscriber, Plan

class PlanSerializer(serializers.ModelSerializer):
    class Meta:
        model = Plan
        fields = ['id', 'name', 'price', 'billing_period']

class SubscriberSerializer(serializers.ModelSerializer):
    plan = PlanSerializer(read_only=True)
    plan_id = serializers.IntegerField(write_only=True)

    class Meta:
        model = Subscriber
        fields = ['id', 'name', 'email', 'phone_number', 'plan', 'plan_id', 'is_active', 'created_at']