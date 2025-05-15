from celery import shared_task
from twilio.rest import Client
from django.conf import settings
from django.core.mail import send_mail
from .models import Subscriber
import logging

logger = logging.getLogger(__name__)

@shared_task
def send_welcome_sms(subscriber_id):
    """
    Celery task to send a welcome SMS to a subscriber.
    """
    try:
        subscriber = Subscriber.objects.get(id=subscriber_id)
        client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
        message = client.messages.create(
            body=f"Hi {subscriber.name}, thanks for subscribing to our livestream service on ChurchPad!",
            from_=settings.TWILIO_PHONE_NUMBER,
            to=subscriber.phone_number,
        )
        logger.info(f"SMS sent to {subscriber.phone_number} for subscriber {subscriber.name}")
    except Subscriber.DoesNotExist:
        logger.error(f"Subscriber with ID {subscriber_id} does not exist.")
    except Exception as e:
        logger.error(f"Failed to send SMS to subscriber ID {subscriber_id}: {str(e)}")


@shared_task
def send_email_task(subject, message, recipient_list):
    """
    Celery task to send emails asynchronously.
    """
    try:
        send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,
            recipient_list,
            fail_silently=False,
        )
        logger.info(f"Email sent to {', '.join(recipient_list)} with subject '{subject}'")
    except Exception as e:
        logger.error(f"Failed to send email to {', '.join(recipient_list)}: {str(e)}")