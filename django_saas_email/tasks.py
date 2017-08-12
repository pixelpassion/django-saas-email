from celery import shared_task

from .models import Mail


@shared_task
def send_asynchronous_mail(mail_uuid, sendgrid_api=False):
    """Send an asynchronous mail by the given ID."""
    try:
        mail = Mail.objects.get(id=mail_uuid)
    except Mail.DoesNotExist:
        raise AttributeError("There is no mail with that UUID")

    mail.send(sendgrid_api=sendgrid_api)
