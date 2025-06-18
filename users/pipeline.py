from common.tasks import send_asynchronous_email_task


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
