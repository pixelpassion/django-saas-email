# -*- coding: utf-8 -*-
from django.views.generic import (
    CreateView,
    DeleteView,
    DetailView,
    UpdateView,
    ListView
)

from .models import Mail, MailTemplate


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
