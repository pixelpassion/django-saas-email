# -*- coding: utf-8 -*-
from django.conf.urls import url

from . import views

app_name = "django_saas_email"

urlpatterns = [
    url(
        regex=r"^Mail/~create/$",
        view=views.MailCreateView.as_view(),
        name="Mail_create",
    ),
    url(
        regex=r"^Mail/(?P<pk>\d+)/~delete/$",
        view=views.MailDeleteView.as_view(),
        name="Mail_delete",
    ),
    url(
        regex=r"^Mail/(?P<pk>\d+)/$",
        view=views.MailDetailView.as_view(),
        name="Mail_detail",
    ),
    url(
        regex=r"^Mail/(?P<pk>\d+)/~update/$",
        view=views.MailUpdateView.as_view(),
        name="Mail_update",
    ),
    url(
        regex=r"^Mail/$",
        view=views.MailListView.as_view(),
        name="Mail_list",
    ),
    url(
        regex=r"^MailTemplate/~create/$",
        view=views.MailTemplateCreateView.as_view(),
        name="MailTemplate_create",
    ),
    url(
        regex=r"^MailTemplate/(?P<pk>\d+)/~delete/$",
        view=views.MailTemplateDeleteView.as_view(),
        name="MailTemplate_delete",
    ),
    url(
        regex=r"^MailTemplate/(?P<pk>\d+)/$",
        view=views.MailTemplateDetailView.as_view(),
        name="MailTemplate_detail",
    ),
    url(
        regex=r"^MailTemplate/(?P<pk>\d+)/~update/$",
        view=views.MailTemplateUpdateView.as_view(),
        name="MailTemplate_update",
    ),
    url(
        regex=r"^MailTemplate/$",
        view=views.MailTemplateListView.as_view(),
        name="MailTemplate_list",
    ),
    url(
        regex=r"^Attachment/~create/$",
        view=views.AttachmentCreateView.as_view(),
        name="Attachment_create",
    ),
    url(
        regex=r"^Attachment/(?P<pk>\d+)/~delete/$",
        view=views.AttachmentDeleteView.as_view(),
        name="Attachment_delete",
    ),
    url(
        regex=r"^Attachment/(?P<pk>\d+)/$",
        view=views.AttachmentDetailView.as_view(),
        name="Attachment_detail",
    ),
    url(
        regex=r"^Attachment/(?P<pk>\d+)/~update/$",
        view=views.AttachmentUpdateView.as_view(),
        name="Attachment_update",
    ),
    url(
        regex=r"^Attachment/$",
        view=views.AttachmentListView.as_view(),
        name="Attachment_list",
    ),
    url(
        regex=r"^TemplateAttachment/~create/$",
        view=views.TemplateAttachmentCreateView.as_view(),
        name="TemplateAttachment_create",
    ),
    url(
        regex=r"^TemplateAttachment/(?P<pk>\d+)/~delete/$",
        view=views.TemplateAttachmentDeleteView.as_view(),
        name="TemplateAttachment_delete",
    ),
    url(
        regex=r"^TemplateAttachment/(?P<pk>\d+)/$",
        view=views.TemplateAttachmentDetailView.as_view(),
        name="TemplateAttachment_detail",
    ),
    url(
        regex=r"^TemplateAttachment/(?P<pk>\d+)/~update/$",
        view=views.TemplateAttachmentUpdateView.as_view(),
        name="TemplateAttachment_update",
    ),
    url(
        regex=r"^TemplateAttachment/$",
        view=views.TemplateAttachmentListView.as_view(),
        name="TemplateAttachment_list",
    ),
]
