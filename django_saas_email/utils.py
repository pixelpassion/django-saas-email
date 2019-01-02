from .models import Mail
from .tasks import send_asynchronous_mail
from django.conf import settings


def create_and_send_mail(**kwargs):
    """Helper method to create and send a mail.

    create_and_send_mail(template_name="hello", context={'name': 'Jens'}, to_address="me@jensneuhaus.de")
    """
    mail = Mail.objects.create_mail(**kwargs)
    send_asynchronous_mail.delay(
        mail.id, sendgrid_api=getattr(settings, "SENDGRID_API_KEY", False)
    )
