from django.contrib import admin
from .models import Plan, Subscriber


@admin.register(Plan)
class PlanAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "price", "billing_period", "stripe_price_id")
    search_fields = ("name", "stripe_price_id")
    list_filter = ("billing_period",)


@admin.register(Subscriber)
class SubscriberAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "name",
        "email",
        "phone_number",
        "plan",
        "is_active",
        "stripe_customer_id",
        "stripe_subscription_id",
    )
    search_fields = (
        "name",
        "email",
        "phone_number",
        "stripe_customer_id",
        "stripe_subscription_id",
    )
    list_filter = ("is_active", "plan")
    readonly_fields = ("stripe_customer_id", "stripe_subscription_id")
