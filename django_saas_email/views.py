# -*- coding: utf-8 -*-
from django.views.generic import (
    CreateView,
    DeleteView,
    DetailView,
    UpdateView,
    ListView
)

from .models import Mail, MailTemplate, Attachment, TemplateAttachment


class MailCreateView(CreateView):
    model = Mail


class MailDeleteView(DeleteView):
    model = Mail


class MailDetailView(DetailView):
    model = Mail


class MailUpdateView(UpdateView):
    model = Mail


class MailListView(ListView):
    model = Mail


class MailTemplateCreateView(CreateView):
    model = MailTemplate


class MailTemplateDeleteView(DeleteView):
    model = MailTemplate


class MailTemplateDetailView(DetailView):
    model = MailTemplate


class MailTemplateUpdateView(UpdateView):
    model = MailTemplate


class MailTemplateListView(ListView):
    model = MailTemplate


class AttachmentCreateView(CreateView):
    model = Attachment


class AttachmentDeleteView(DeleteView):
    model = Attachment


class AttachmentDetailView(DetailView):
    model = Attachment


class AttachmentUpdateView(UpdateView):
    model = Attachment


class AttachmentListView(ListView):
    model = Attachment


class TemplateAttachmentCreateView(CreateView):
    model = TemplateAttachment


class TemplateAttachmentDeleteView(DeleteView):
    model = TemplateAttachment


class TemplateAttachmentDetailView(DetailView):
    model = TemplateAttachment


class TemplateAttachmentUpdateView(UpdateView):
    model = TemplateAttachment


class TemplateAttachmentListView(ListView):
    model = TemplateAttachment
