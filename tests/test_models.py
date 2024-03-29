#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
test_django-saas-email
------------

Tests for `django-saas-email` models module.
"""
import base64
import pathlib
import tempfile

import mock
from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.files.uploadedfile import SimpleUploadedFile
from django.template import Context
from django.test import TestCase, override_settings
from override_storage import override_storage
from python_http_client import Client

from django_saas_email.models import Attachment, Mail, MailTemplate, TemplateAttachment


class CreateMailTest(TestCase):
    def setUp(self):
        # Create a MailTemplate for the test email to use
        template = MailTemplate(
            name="test_template",
            subject="test_subject_template",
            html_template="<p>This is an HTML template {{ name }}</p>",
            text_template="Text template {{ name }}",
        )
        template.save()

        # Valid mail fields
        self.valid_template = template
        self.valid_to_address = "mail-test@mailtest.com"
        self.valid_from_address = "mail-test@mailtest.com"
        self.valid_subject = "Hello there {{ name }}"
        self.valid_context = {"name": "Max"}

    def create_mail(
        self,
        template=None,
        context=None,
        to_address=None,
        from_address="Default",
        subject="Default",
    ):
        """Create and return Mail object with default valid fields."""

        return Mail.objects.create_mail(
            template if template else self.valid_template,
            context if context else self.valid_context,
            to_address if to_address else self.valid_to_address,
            from_address if from_address != "Default" else self.valid_from_address,
            subject if subject != "Default" else self.valid_subject,
        )

    def test_create_mail_with_required_fields_only(self):
        """
        Call Mail.objects.create_mail with valid required arguments
        should succeed.
        """

        mail_with_required_fields_only = self.create_mail(
            from_address=None, subject=None
        )

        # Make sure arguments were recorded correctly
        self.assertEqual(mail_with_required_fields_only.template, self.valid_template)
        self.assertEqual(mail_with_required_fields_only.context, self.valid_context)
        self.assertEqual(
            mail_with_required_fields_only.to_address, self.valid_to_address
        )

        # From address should be the default
        self.assertEqual(
            mail_with_required_fields_only.from_address, settings.DEFAULT_FROM_EMAIL
        )

        # Subject should be set to None
        self.assertIsNone(mail_with_required_fields_only.subject)

    def test_create_mail_with_optional_fields(self):
        """Call Mail.objects.create_mail with optional arguments should succeed."""

        mail_with_optional_fields = self.create_mail()

        # Make sure arguments were recorded correctly
        self.assertEqual(mail_with_optional_fields.template, self.valid_template)
        self.assertEqual(mail_with_optional_fields.context, self.valid_context)
        self.assertEqual(mail_with_optional_fields.to_address, self.valid_to_address)
        self.assertEqual(
            mail_with_optional_fields.from_address, self.valid_from_address
        )
        self.assertEqual(mail_with_optional_fields.subject, self.valid_subject)

    def test_create_mail_with_invalid_template(self):
        """Call Mail.objects.create_mail with invalid template should fail."""

        with self.assertRaises(
            ValueError, msg="Invalid template name should raise ValueError"
        ):
            self.create_mail(template="really bad template name")

    def test_create_mail_with_invalid_context(self):
        """Call Mail.objects.create_mail with invalid context should fail."""

        # Invalid context should raise ValueError
        with self.assertRaises(
            ValueError, msg="Invalid context should raise ValueError"
        ):
            self.create_mail(context="Not a dictionary")

    def test_create_mail_with_invalid_to_address(self):
        """Call Mail.objects.create_mail with invalid to_address should fail."""

        with self.assertRaises(
            ValueError, msg="Invalid to address should raise ValueError"
        ):
            self.create_mail(to_address="invalid email address")

    def test_create_mail_with_invalid_from_address(self):
        """Call Mail.objects.create_mail with invalid from_address should fail."""

        with self.assertRaises(
            ValueError, msg="Invalid from address should raise ValueError"
        ):
            self.create_mail(from_address="invalid email address")

    def tearDown(self):
        self.valid_template = None
        self.valid_to_address = None
        self.valid_from_address = None
        self.valid_subject = None
        self.valid_context = None


@override_settings(SENDGRID_API_KEY="test-api-key")
class SendMailTest(TestCase):
    def setUp(self):
        # Create a MailTemplate for the test email to use
        template = MailTemplate(
            name="test_template",
            subject="test_subject_template",
            html_template="<p>This is an HTML template {{ name }}</p>",
            text_template="Text template {{ name }}",
        )
        template.save()

        # Create valid Mail object
        self.mail = Mail.objects.create_mail(
            "test_template",
            {"name": "Max"},
            "mailtest@sink.sendgrid.net",
            "test@example.com",
        )

    def test_send_mail_anymail(self):
        """Call mail.send().

        Make sure mail is actually sent.
        """
        self.mail.send()

    def tearDown(self):
        self.mail = None


class SendMailInfoTest(TestCase):
    def setUp(self):
        # Create a MailTemplate for the test email to use
        template = MailTemplate(
            name="test_template",
            subject="test_subject_template",
            html_template="<p>This is an HTML template {{ name }}</p>",
            text_template="Text template {{ name }}",
        )
        template.save()

        # Create valid Mail object
        self.mail = Mail.objects.create_mail(
            "test_template",
            {"name": "Max"},
            "mailtest@sink.sendgrid.net",
            "test@example.com",
            subject="Custom subject",
        )

    def test_mail_with_template_name(self):

        # Send the mail and record time sent
        self.mail.send()

    def test_mail_with_template_object(self):

        template = MailTemplate.objects.get(name="test_template")
        self.mail = Mail.objects.create_mail(
            template,
            {"name": "Max"},
            "mailtest@sink.sendgrid.net",
            "test@example.com",
            subject="Custom subject",
        )

        # Send the mail and record time sent
        self.mail.send()

    def test_mail_with_text(self):
        MailTemplate.objects.get(name="test_template")
        self.mail = Mail.objects.create_mail(
            None,
            {"name": "Max"},
            "mailtest@sink.sendgrid.net",
            "test@example.com",
            subject="Custom subject",
            text="Test text",
        )

        # Send the mail and record time sent
        self.mail.send()

    def test_send_mail_subject(self):
        """Check that correct subject is recorded."""
        self.assertEqual(
            self.mail.subject, "Custom subject", msg="Mail subject recorded incorrectly"
        )

    def test_send_mail_date(self):
        """Check that correct sent datetime is recorded."""
        # self.assertTrue(
        #     (self.mail.time_sent - timezone.now()) < timedelta(seconds=2),
        #     msg="Mail time_sent recorded inaccurately"
        # )

    def test_both_template_and_text_specified(self):
        template = MailTemplate.objects.get(name="test_template")
        with self.assertRaises(ValidationError):
            self.mail = Mail.objects.create_mail(
                template,
                {"name": "Max"},
                "mailtest@sink.sendgrid.net",
                "test@example.com",
                subject="Custom subject",
                text="Text",
            )

    def test_none_of_template_and_text_specified(self):
        with self.assertRaises(ValidationError):
            self.mail = Mail.objects.create_mail(
                None,
                {"name": "Max"},
                "mailtest@sink.sendgrid.net",
                "test@example.com",
                subject="Custom subject",
            )

    def test_save_both_template_and_text_specified(self):
        template = MailTemplate.objects.get(name="test_template")
        with self.assertRaises(ValidationError):
            Mail.objects.create(
                template=template,
                context={},
                from_address="test@example.com",
                to_address="mailtest@sink.sendgrid.net",
                subject="Custom subject",
                text="Text",
            )

    def test_save_none_of_template_and_text_specified(self):
        with self.assertRaises(ValidationError):
            Mail.objects.create(
                template=None,
                context={},
                from_address="test@example.com",
                to_address="mailtest@sink.sendgrid.net",
                subject="Custom subject",
            )

    def tearDown(self):
        self.mail = None


@override_settings(SENDGRID_API_KEY="test-api-key")
class MailAttachmentsSendTest(TestCase):
    file_contents = b"Here the file contents"

    def setUp(self):
        self.mail_template = MailTemplate(
            name="test_template",
            subject="Message for {{ name }}",
            html_template="<p><b>Hello</b>, {{ name }}!</p>",
        )
        self.mail_template.save()
        self.context = Context({"name": "Max"})
        self.media_root_old = settings.MEDIA_ROOT
        self.temp_dir = pathlib.Path(tempfile.mkdtemp())
        settings.MEDIA_ROOT = self.temp_dir
        self.attachment = Attachment(
            name="attachment1",
            attached_file=SimpleUploadedFile("input.txt", self.file_contents),
        )
        self.attachment.save()
        TemplateAttachment.objects.create(
            template=self.mail_template, attachment=self.attachment
        )

    @mock.patch.object(Client, "post", create=True)
    def testGridMailSend(self, post):
        self.mail = Mail.objects.create_mail(
            self.mail_template,
            {"name": "Max"},
            "mailtest@sink.sendgrid.net",
            "test@example.com",
            subject="Custom subject",
            selected_attachments=[self.attachment],
        )

        # Send the mail and record time sent
        self.mail.send(sendgrid_api=True)
        args, kwargs = post.call_args
        content = base64.b64decode(kwargs["request_body"]["attachments"][0]["content"])
        self.assertEqual(content, self.file_contents)

    @mock.patch.object(Client, "post", create=True)
    def testGridMailSendNoTemplateAttachments(self, post):
        email = "mailtest@sink.sendgrid.net"
        email_from = "test@example.com"
        subject = "Custom subject"
        att = Attachment(
            name="attachment2",
            attached_file=SimpleUploadedFile("input.txt", b"Some another attachment"),
        )
        att.save()
        self.mail = Mail.objects.create_mail(
            self.mail_template,
            {"name": "Max"},
            email,
            email_from,
            subject=subject,
            selected_attachments=[att],
        )
        self.mail.send(sendgrid_api=True)
        args, kwargs = post.call_args
        request_body = kwargs["request_body"]
        personalizations = request_body["personalizations"]
        self.assertEqual(len(personalizations), 1)
        self.assertEqual(personalizations[0]["to"][0]["email"], email)
        self.assertEqual(request_body["from"]["email"], email_from)
        # Check if Template attachment is not present
        attachment_contents = list(
            map(base64.b64decode, [a["content"] for a in request_body["attachments"]])
        )
        self.assertFalse(self.file_contents in attachment_contents)
        self.assertTrue(att.attached_file.read() in attachment_contents)

    def testMailSend(self):
        self.mail = Mail.objects.create_mail(
            self.mail_template,
            {"name": "Max"},
            "mailtest@sink.sendgrid.net",
            "test@example.com",
            subject="Custom subject",
            selected_attachments=[self.attachment],
        )

        # Send the mail and record time sent
        self.mail.send()


class MailTemplateTest(TestCase):
    def setUp(self):
        # Create valid MailTemplate
        self.mail_template = MailTemplate(
            name="test_template",
            subject="Message for {{ name }}",
            html_template="<p><b>Hello</b>, {{ name }}!</p>",
        )
        self.mail_template.save()

        self.context = Context({"name": "Max"})

    def test_render_subject(self):
        """Check that the correct subject line is generated."""
        self.assertEqual(
            self.mail_template.render_subject(self.context),
            "Message for Max",
            msg="Mail template generated incorrect subject",
        )

    def test_make_output(self):
        """
        Check that the correct html and text output is produced when both
        templates are provided.
        """
        self.mail_template.text_template = "Hello, {{ name }}!"
        self.mail_template.save()

        self.assertInHTML(
            "<p><b>Hello</b>, Max!</p>",
            self.mail_template.render_with_context(self.context)["html"],
        )
        self.assertInHTML(
            "Hello, Max!", self.mail_template.render_with_context(self.context)["text"]
        )

    def test_html_to_text(self):
        """Check that html_to_text() produces correct output."""
        test_html = """
        <p><strong>Bold test</strong> and
        <em>Italics test</p>\n
        <p>And finally a <a href='https://www.example.com/'>Link test</a>
        """
        test_expected_output = (
            "**Bold test** and "
            "_Italics test\n\n"
            "And finally a [Link test](https://www.example.com/)\n\n"
        )
        self.assertInHTML(
            test_expected_output, self.mail_template.html_to_text(test_html)
        )

    def test_make_output_html_only(self):
        """
        Check that the correct html and text output is produced when
        only html template is provided.
        """
        self.assertInHTML(
            "<p><b>Hello</b>, Max!</p>",
            self.mail_template.render_with_context(self.context)["html"],
        )
        self.assertInHTML(
            "**Hello**, Max!\n\n",
            self.mail_template.render_with_context(self.context)["text"],
        )

    @override_settings(DJANGO_SASS_EMAIL_FOOTER=None)
    def test_use_default_footer(self):
        self.assertInHTML(
            "<a href='#'>Your Email Footer</a>",
            self.mail_template.render_with_context(self.context)["html"],
        )

    @override_settings(DJANGO_SASS_EMAIL_FOOTER="<a href='#'>Follow me now</a>")
    def test_use_django_saas_email_footer_setting_if_set(self):
        self.assertInHTML(
            "<a href='#'>Follow me now</a>",
            self.mail_template.render_with_context(self.context)["html"],
        )

    def test_mail_context(self):
        pass

    def tearDown(self):
        self.mail_template = None


@override_storage()
class AttachmentTest(TestCase):
    file_contents = b"Here the file contents"

    def setUp(self):
        self.mail_template = MailTemplate(
            name="test_template",
            subject="Message for {{ name }}",
            html_template="<p><b>Hello</b>, {{ name }}!</p>",
        )
        self.mail_template.save()
        self.attachment = Attachment(
            name="attachment1",
            attached_file=SimpleUploadedFile("input.txt", self.file_contents),
        )
        self.attachment.save()
        TemplateAttachment.objects.create(
            template=self.mail_template, attachment=self.attachment
        )

    def testAttachmentUploaded(self):
        self.assertEqual(self.attachment.attached_file.read(), self.file_contents)

    def test_preselected_attachments(self):
        self.assertEqual(
            list(self.mail_template.preselected_attachments.all()), [self.attachment]
        )
