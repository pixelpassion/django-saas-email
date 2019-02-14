from django.apps import apps
from django.contrib import admin
from django.utils.translation import ugettext_lazy as _
from django.conf import settings

from .models import Mail, MailTemplate, Attachment, TemplateAttachment
from .tasks import send_asynchronous_mail
from .utils import create_and_send_mail
from django.core.exceptions import ImproperlyConfigured


class TemplateAttachmentInline(admin.TabularInline):
    model = TemplateAttachment


@admin.register(Attachment)
class AttachmentAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')
    ordering = ('-time_created',)
    search_fields = ('name', )
    readonly_fields = ('time_created', )


@admin.register(MailTemplate)
class MailTemplateAdmin(admin.ModelAdmin):

    def test_mail_template(self, request, queryset):

        mails_sent = 0

        if not settings.DJANGO_SAAS_TEST_EMAIL_ADDRESS:
            raise ImproperlyConfigured(
                "You need to add DJANGO_SAAS_TEST_EMAIL_ADDRESS=youremailaddress@example.com to test emails.")

        for template in queryset:
            create_and_send_mail(
                template_name=template.name, context={}, to_address=settings.DJANGO_SAAS_TEST_EMAIL_ADDRESS)

            mails_sent += 1

        if mails_sent == 1:
            message_bit = _("1 Mail template was")
        else:
            message_bit = _("%s Mail templates were") % mails_sent
        self.message_user(request, "%s tested" % message_bit)

    test_mail_template.short_description = "Send test mail now"

    list_display = ('name', 'subject')
    search_fields = []
    ordering = ('name',)
    actions = [test_mail_template, ]
    inlines = [TemplateAttachmentInline, ]


model_class_name = getattr(settings, "DJANGO_SAAS_EMAIL_MAIL_MODEL", "django_saas_email.mail")
model_class = apps.get_model(*model_class_name.split())


@admin.register(model_class)
class MailAdmin(admin.ModelAdmin):

    def send_mail_now(self, request, queryset):

        mails_sent = 0

        for mail in queryset:
            send_asynchronous_mail(str(mail.id), settings.USE_SENDGRID)
            mails_sent += 1

        if mails_sent == 1:
            message_bit = _("1 Mail was")
        else:
            message_bit = _("%s Mails were") % mails_sent
        self.message_user(request, "%s sent" % message_bit)

    send_mail_now.short_description = "Send mail now"

    list_display = ('id', 'time_created', 'from_address', 'to_address', 'cc_address', 'template', 'subject', 'context',)
    search_fields = ['from_address', 'to_address', 'cc_address', 'subject', 'context', ]
    ordering = ('-time_created',)
    list_filter = ('time_created', 'template')

    actions = [send_mail_now, ]

    readonly_fields = (
        'time_created', 'time_sent', 'time_delivered', 'used_backend', 'delivery_mail_id', 'delivery_status')


