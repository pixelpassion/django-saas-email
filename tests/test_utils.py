import celery

from django.core import mail
from django.test import TestCase

from django_saas_email.utils import create_and_send_mail


class TestCreateAndSendMail(TestCase):

    def setUp(self):
        celery.current_app.conf.task_always_eager = True

    def test_create_and_send_mail(self):
        create_and_send_mail(template_name="hello", context={'name': 'Jens'}, to_address="me@jensneuhaus.de")
        assert len(mail.outbox) == 1
