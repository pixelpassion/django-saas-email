# -*- coding: utf-8
from __future__ import absolute_import, unicode_literals

from django.conf.urls import include, url

urlpatterns = [
    url(r"^", include("django_saas_email.urls", namespace="django_saas_email")),
]
