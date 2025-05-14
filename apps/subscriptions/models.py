from django.db import models
from apps.common.models import TimeStampedModel
from django.utils.translation import gettext_lazy as _


class Plan(TimeStampedModel):
    class BillingPeriod(models.TextChoices):
        MONTHLY = "month", _("Monthly")
        YEARLY = "year", _("Yearly")

    name = models.CharField(verbose_name=_("Name"), max_length=100)
    stripe_price_id = models.CharField(
        verbose_name=_("Stripe Price ID"), max_length=100
    )
    price = models.DecimalField(
        verbose_name=_("Price"), max_digits=10, decimal_places=2
    )
    billing_period = models.CharField(
        verbose_name=_("Billing Period"),
        max_length=10,
        choices=BillingPeriod.choices,
        default=BillingPeriod.MONTHLY,
    )

    def __str__(self):
        return self.name


class Subscriber(TimeStampedModel):
    name = models.CharField(verbose_name=_("Name"), max_length=100)
    email = models.EmailField(verbose_name=_("Email"), unique=True)
    phone_number = models.CharField(verbose_name=_("Phone Number"), max_length=20)
    plan = models.ForeignKey(Plan, on_delete=models.PROTECT)
    is_active = models.BooleanField(default=False)
    stripe_customer_id = models.CharField(max_length=100, unique=True)
    stripe_subscription_id = models.CharField(max_length=100, unique=True)

    class Meta:
        indexes = [
            models.Index(fields=["email"]),
            models.Index(fields=["is_active"]),
            models.Index(fields=["plan"]),
        ]

    def __str__(self):
        return self.email
