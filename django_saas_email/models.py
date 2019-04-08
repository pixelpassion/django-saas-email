# -*- coding: utf-8 -*-
import base64
import json
import uuid
import os

import html2text
import html2text.config
import sendgrid
from django.utils.safestring import mark_safe
from python_http_client import HTTPError
from sendgrid.helpers.mail import Email, Content, Mail as HelperMail, Attachment as HelperAttachment

from django.conf import settings
from tinymce import models as tinymce_models

from .logger import logger

try:
    from django.contrib.postgres.fields import JSONField
except:
    from jsonfield import JSONField

from django.core.exceptions import ImproperlyConfigured, ValidationError
from django.core.mail import EmailMessage, EmailMultiAlternatives
from django.core.validators import validate_email
from django.db import models
from django.template import Context, Template
from django.template import engines
from django.template.utils import InvalidTemplateEngineError
from django.template.loader import render_to_string
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _


html2text.config.UNICODE_SNOB = 1  # Do not convert umlauts to umlautless characters


class AbstractMailTemplate(models.Model):
    html_template_file = "django_saas_email/email_base.html"

    name = models.CharField(
        _("Template name"), help_text=_("Template name; a short all-lowercase string"), max_length=100, unique=True
    )

    subject = models.CharField(
        _("Email subject line template"), help_text=_('A format string like "Hello {}"; required'), max_length=200
    )

    # HTML field for the html
    html_template = tinymce_models.HTMLField(
        _("HTML template (required)"), help_text=_("The HTML template, written with Django's template syntax; required")
    )

    text_template = models.TextField(
        _("Text template (optional)"),
        help_text=_(
            "This is an optional field for adding a custom text-only version of this template. "
            "If left blank, the plaintext email will be generated dynamically from the HTML when needed."
        ),
        default="",
        null=True,
        blank=True,
    )

    preselected_attachments = models.ManyToManyField("Attachment", through="TemplateAttachment", blank=True)

    sender_email = models.EmailField(
        null=True,
        blank=True,
        help_text=_(
            "Email to use as sender address when the template is used. If not set then default address is used"
        ),
    )

    class Meta:
        abstract = True

    def __str__(self):
        return "%s" % self.name

    @property
    def backend(self):
        try:
            return self._backend
        except AttributeError:
            try:
                self._backend = engines["email"]
            except InvalidTemplateEngineError:
                self._backend = None
            return self._backend

    @staticmethod
    def get_footer():
        """The used footer in the email."""
        return getattr(settings, "DJANGO_SASS_EMAIL_FOOTER", None)

    def render_subject(self, context):
        """Take a list of values (inputs) and format the subject template, returning the subject."""
        return Template(self.subject, engine=self.backend.engine).render(context)

    def render_with_context(self, context, plain_text_context=None):
        """Return a dictionary containing two strings, the HTML and plaintext output.

        This output is generated by filling in the templates using the provided context.
        If the text_template field is empty, it will dynamically generate the text version from the HTML output.
        """
        if plain_text_context is None:
            plain_text_context = {k: mark_safe(v) for k, v in context.items()}
        # Rendering of EMAIL_CONTENT
        email_content_html = Template(self.html_template, engine=self.backend.engine).render(context)

        # Context for HTML Template, including EMAIL_CONTENT
        html_context = {
            "EMAIL_CONTENT": email_content_html,
            "EMAIL_SUBJECT": self.render_subject(context),
            "EMAIL_FOOTER": self.get_footer(),
        }

        if self.backend:
            template = self.backend.get_template(self.html_template_file)
            html_output = template.render(html_context)
        else:
            html_output = render_to_string(self.html_template_file, html_context)

        if self.text_template:
            text_output = Template(self.text_template, engine=self.backend.engine).render(plain_text_context)
        else:
            text_output = self.html_to_text(email_content_html)

        return {"html": html_output, "text": text_output}

    def html_to_text(self, html_string):
        """A helper method that converts a string containing HTML into a string with plaintext only.

        This is currently done with html2text, which converts HTML into valid Markdown.
        If no text_template exists, make_output() will use this method to generate the text-only output.
        This method should not be called externally.
        """
        h = html2text.HTML2Text(bodywidth=0)
        return h.handle(html_string)


class MailTemplate(AbstractMailTemplate):
    pass


class AbstractAttachment(models.Model):
    name = models.CharField(max_length=100)
    attached_file = models.FileField(upload_to="email-attachments")
    time_created = models.DateTimeField(verbose_name=_("Creation time"), default=timezone.now, editable=False)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = _("attachment")
        verbose_name_plural = _("attachments")
        abstract = True


class Attachment(AbstractAttachment):
    pass


class TemplateAttachment(models.Model):
    attachment = models.ForeignKey(Attachment, on_delete=models.CASCADE, related_name="templates")
    template = models.ForeignKey(MailTemplate, on_delete=models.CASCADE, related_name="attachments")

    class Meta:
        verbose_name = _("Preselected attachment")
        verbose_name_plural = _("Preselected attachments")


class MailManager(models.Manager):
    def create_mail(
        self,
        template_name=None,
        context=None,
        to_address=None,
        to_name=None,
        from_address=None,
        from_name=None,
        subject=None,
        selected_attachments=None,
        text=None,
        cc_address=None,
        bcc_address=None,
    ):
        """Create a Mail object with proper validation.

        e.g.
        mail = Mail.objects.create_mail("hello", {'name': 'Jens'},"me@jensneuhaus.de")
        mail.send()
        """

        if (template_name is None) == (text is None):
            raise ValidationError("Exactly one of `text` or `template_name` must be specified")
        if not to_address:
            raise ValidationError("`to_address` must be specified")
        if template_name:
            if not isinstance(template_name, MailTemplate):
                try:
                    template = MailTemplate.objects.get(name__iexact=template_name)
                except MailTemplate.DoesNotExist:
                    raise ValueError("{} is not a valid Template name".format(template_name))
            else:
                template = template_name
            if not context:
                raise ValidationError("`context` must be specified when using template")

            try:
                context_string = json.dumps(context)
                context_json = json.loads(context_string)
            except ValueError:
                raise ValueError("The given context is not valid: {}".format(context))

            if not isinstance(context, dict):
                raise ValueError("The given context is not a dictionary: {}".format(context))
        else:
            template = None
            context_json = None

        if from_address is None:
            if template.sender_email:
                from_address = template.sender_email
            else:
                from_address = settings.DEFAULT_FROM_EMAIL

        try:
            validate_email(from_address)
        except ValidationError:
            raise ValueError("The given email is not valid: {}".format(from_address))

        try:
            validate_email(to_address)
        except ValidationError:
            raise ValueError("The given email is not valid: {}".format(to_address))

        mail = self.create(
            template=template,
            context=context_json,
            from_address=from_address,
            from_name=from_name,
            to_address=to_address,
            to_name=to_name,
            cc_address=cc_address,
            bcc_address=bcc_address,
            subject=subject,
            text=text,
        )

        if selected_attachments is not None:
            for attachment in selected_attachments:
                mail.selected_attachments.add(attachment)

        return mail


class AbstractMail(models.Model):

    id = models.UUIDField(_("ID"), primary_key=True, unique=True, default=uuid.uuid4, editable=False)

    from_address = models.EmailField(
        _("Sender email address"), help_text=_("The 'from' field of the email"), null=False, blank=False
    )

    from_name = models.CharField(
        max_length=100, verbose_name=("Sender name"), help_text=_("Email sender name"), null=True, blank=True
    )

    to_address = models.EmailField(
        _("Recipient email address"), help_text=_("The 'to' field of the email"), null=False, blank=False
    )

    to_name = models.CharField(
        max_length=100, verbose_name=_("Recipient name"), help_text=_("Email recipient name"), null=True, blank=True
    )

    cc_address = models.EmailField(
        _("CC email address"), help_text=_("The 'cc' field of the email"), null=True, blank=True
    )

    bcc_address = models.EmailField(
        _("BCC email address"), help_text=_("The 'bcc' field of the email"), null=True, blank=True
    )

    # delivery_service (Sendgrid etc. - should be a CharField with Options)
    delivery_mail_id = models.IntegerField(
        _("Unique mail sender ID"),
        help_text=_("The ID is saved after correct sending"),
        null=True,
        blank=True,
        editable=False,
    )

    # The following should maybe be a CharField - depending on the anymail output
    delivery_status = models.IntegerField(
        _("Status of Mail sender"), help_text=_("The Mail sender status"), null=True, blank=True, editable=False
    )

    template = models.ForeignKey(
        MailTemplate,
        verbose_name=_("Used Mail template"),
        help_text=_("The used template"),
        null=True,
        blank=True,
        on_delete=models.CASCADE,
    )

    text = models.TextField(verbose_name=_("Message text (plain)"), null=True, blank=True)

    subject = models.CharField(
        _("Email Subject line"), help_text=_("Subject line for a mail"), max_length=500, null=True, blank=True
    )

    context = JSONField(
        _("Data of email context"),
        help_text=_("JSON dump of context dictionary used to fill in templates"),
        null=True,
        blank=True,
    )

    time_created = models.DateTimeField(
        _("Creation time"), help_text=_("When was the mail created?"), default=timezone.now, editable=False
    )

    time_sent = models.DateTimeField(
        _("Sent time"), help_text=_("When was the mail send via the backend?"), null=True, blank=True, editable=False
    )
    time_delivered = models.DateTimeField(
        _("Delivery time"),
        help_text=_("Actual delivery time by the email backend"),
        null=True,
        blank=True,
        editable=False,
    )

    used_backend = models.CharField(
        _("E-Mail Backend"),
        help_text=_("Which email backend was used for sending?"),
        null=True,
        blank=True,
        max_length=128,
        editable=False,
    )

    selected_attachments = models.ManyToManyField(Attachment, blank=True)

    objects = MailManager()

    class Meta:
        abstract = True

    def __str__(self):
        return "%s to %s" % (self.template, self.to_address)

    @classmethod
    def get_extra_context(cls):
        """Placeholder to add extra context."""
        return {}

    def get_plain_text_context(self):
        context = {k: mark_safe(v) for k, v in self.context.items()}
        return Context({**context, **self.get_extra_context()})

    def get_context(self):
        return Context({**self.context, **self.get_extra_context()})

    def save(self, *args, **kwargs):
        if (self.template is None) == (self.text is None):
            raise ValidationError("Exactly one of `template` or `text` must be specified")
        super().save(*args, **kwargs)

    def render_mail(self):
        """Check for existing MailTemplate. Text is needed, HTML is optional.

        Returns a dictionary containing subject, text output, and html output.
        """
        if self.template:
            context = self.get_context()
            plain_text_context = self.get_plain_text_context()

            try:
                mail_template = MailTemplate.objects.get(name=self.template)
            except MailTemplate.DoesNotExist:
                raise ImproperlyConfigured("No mail template found with name: {}".format(self.template))

            if self.subject:
                rendered_subject = Template(self.subject).render(plain_text_context)
            else:
                rendered_subject = mail_template.render_subject(plain_text_context)

            output_dict = mail_template.render_with_context(context, plain_text_context)
            output_dict["subject"] = rendered_subject

            return output_dict
        else:
            return {"subject": self.subject, "text": self.text, "html": None}

    def send(self, sendgrid_api=False):
        """Send the mail using data from the Mail object.

        It can be called directly, but is usually called asynchronously with tasks.send_asynchronous_mail.

        sendgrid_api=True uses the sendgrid API directly (with bypassing django-anymail)
        """
        rendered_output = self.render_mail()

        html_content = rendered_output["html"]
        txt_content = rendered_output["text"]
        rendered_subject = rendered_output["subject"]

        if sendgrid_api:

            if not settings.SENDGRID_API_KEY:
                raise ImproperlyConfigured("No SENDGRID_API_KEY set.")

            sg = sendgrid.SendGridAPIClient(settings.SENDGRID_API_KEY)
            from_email = Email(self.from_address, self.from_name)
            content = Content("text/plain", txt_content)
            init_kwargs = {"from_email": from_email, "subject": rendered_subject, "plain_text_content": content}
            to_emails = [sendgrid.To(self.to_address, self.to_name)]
            if self.cc_address and self.to_address != self.cc_address:
                to_emails.append(sendgrid.Cc(self.cc_address))
            if (
                self.bcc_address
                and self.to_address != self.bcc_address
                and (not self.cc_address or self.cc_address != self.bcc_address)
            ):
                to_emails.append(sendgrid.Bcc(self.bcc_address))
            init_kwargs["to_emails"] = to_emails
            mail = HelperMail(**init_kwargs)
            for attachment in self.selected_attachments.all():
                ha = HelperAttachment()
                ha.content = base64.b64encode(attachment.attached_file.read()).decode("ascii")
                ha.filename = os.path.basename(attachment.attached_file.name)
                ha.disposition = "attachment"
                mail.add_attachment(ha)

            try:
                response = sg.send(mail)
            except HTTPError as e:
                logger.warning("Error sending mail: status_code={}, body={}".format(e.status_code, e.body))
                raise

            logger.debug("Email with UUID {} was sent with Sendgrid API.".format(self.id))
            logger.debug(
                "Response Status Code: {}, Body: {}, Headers: {}".format(
                    response.status_code, response.body, response.headers
                )
            )

            self.used_backend = "Sendgrid ({})".format(response.status_code)

        else:
            if html_content:
                msg = EmailMultiAlternatives(rendered_subject, txt_content, self.from_address, [self.to_address])
                msg.attach_alternative(html_content, "text/html")

            else:
                msg = EmailMessage(rendered_subject, txt_content, self.from_address, [self.to_address])
            for attachment in self.selected_attachments.all():
                msg.attach(attachment.attached_file.name, content=attachment.attached_file.read())

            msg.send()

            logger.info("Email with UUID {} was sent.".format(self.id))

            self.used_backend = settings.EMAIL_BACKEND

        self.time_sent = timezone.now()
        self.save()


class Mail(AbstractMail):
    pass
