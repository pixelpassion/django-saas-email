from celery import shared_task
from django.conf import settings
from django.apps import apps
from .models import Mail


@shared_task
def send_asynchronous_mail(mail_uuid, sendgrid_api=False):
    """Send an asynchronous mail by the given ID."""
    try:
        app_model_name = settings.DJANGO_SAAS_EMAIL_MAIL_MODEL
    except AttributeError:
        mail_model = Mail
    else:
        app_label, model_name = app_model_name.split('.')
        mail_model = apps.get_model(app_label, model_name)
    try:
        mail = mail_model.objects.get(id=mail_uuid)
    except Mail.DoesNotExist:
        raise AttributeError("There is no mail with that UUID")

    mail.send(sendgrid_api=sendgrid_api)
