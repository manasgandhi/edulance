from common.tasks import send_asynchronous_email_task
from social_django.models import UserSocialAuth


def send_welcome_email(backend, user, response, *args, **kwargs):
    """
    Helper function to send welcome email.
    """
    if kwargs.get("is_new"):
        mail_subject = "Welcome to Edulance"
        message = f"""
        Hi {user.first_name},

        Thank you very much for registering on edulance.

        Gracefully,
        Edulance Team
        """

        send_asynchronous_email_task.delay(mail_subject, message, user.email)


def get_user_avatar(backend, user, response, *args, **kwargs):
    try:
        social = user.social_auth.get(provider="google-oauth2")
        user.avatar_url = social.extra_data["picture"]
        user.save()
    except UserSocialAuth.DoesNotExist:
        return None
