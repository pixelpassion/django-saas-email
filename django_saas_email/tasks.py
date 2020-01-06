from django.conf import settings
from django.apps import apps
from .models import Mail

task_queue = getattr(settings, "DJANGO_SAAS_EMAIL_TASK_QUEUE", "celery")
decorator_kwargs = getattr(settings, "DJANGO_SAAS_EMAIL_DECORATOR_KWARGS", {})

if task_queue == "celery":
    from celery import shared_task as task_decorator
elif task_queue == "rq":
    from django_rq import job as task_decorator
else:
    raise RuntimeError("Only `celery` and `rq` task queues are supported.")


@task_decorator(**decorator_kwargs)
def send_asynchronous_mail(mail_uuid, sendgrid_api=False):
    """Send an asynchronous mail by the given ID."""
    try:
        app_model_name = settings.DJANGO_SAAS_EMAIL_MAIL_MODEL
    except AttributeError:
        mail_model = Mail
    else:
        app_label, model_name = app_model_name.split(".")
        mail_model = apps.get_model(app_label, model_name)
    try:
        mail = mail_model.objects.get(id=mail_uuid)
    except Mail.DoesNotExist:
        raise AttributeError("There is no mail with that UUID")

    mail.send(sendgrid_api=sendgrid_api)
