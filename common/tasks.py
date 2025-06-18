from celery import shared_task
from django.core.mail import send_mail
from django.conf import settings
from datetime import datetime
import logging

logger = logging.getLogger("celery")
logger_beat = logging.getLogger("celery_beat")


@shared_task
def send_asynchronous_email_task(mail_subject, message, recipient_email):
    """
    Task to send a verification email asynchronously.
    """
    send_mail(
        mail_subject,
        message,
        settings.DEFAULT_FROM_EMAIL,
        [recipient_email],
    )
    logger.info("Mail sent successfully.")


@shared_task
def test_beat_task():
    print(__name__)
    print("Logging not working fine")
    logger_beat.info(f"[{datetime.now()}] Celery Beat test task ran successfully.")
