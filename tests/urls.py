# -*- coding: utf-8
from __future__ import absolute_import, unicode_literals

from django.urls import include, re_path

urlpatterns = [
    re_path(r"^", include("django_saas_email.urls", namespace="django_saas_email")),
]
