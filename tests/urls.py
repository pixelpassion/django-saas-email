# -*- coding: utf-8
from __future__ import unicode_literals, absolute_import

from django.conf.urls import url, include

from django_saas_email.urls import urlpatterns as django_saas_email_urls

urlpatterns = [
    url(r'^', include(django_saas_email_urls, namespace='django_saas_email')),
]
