from celery import shared_task
from twilio.rest import Client
from django.conf import settings
from .models import Subscriber

@shared_task
def send_welcome_sms(subscriber_id):
    try:
        subscriber = Subscriber.objects.get(id=subscriber_id)
        client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
        message = client.messages.create(
            body=f"Hi {subscriber.name}, thanks for subscribing to our livestream service on ChurchPad!",
            from_=settings.TWILIO_PHONE_NUMBER,
            to=subscriber.phone_number
        )
        print( f"SMS sent to {subscriber.phone_number}")
    except Exception as e:
        return str(e)