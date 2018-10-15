# -*- coding: utf-8
from __future__ import unicode_literals, absolute_import

from django.conf.urls import url, include
from django.contrib import admin
from django.contrib.staticfiles.urls import staticfiles_urlpatterns


urlpatterns = [
    url(r'^', include('django_saas_email.urls', namespace='django_saas_email')),
    url(r'^admin/', admin.site.urls)
]

urlpatterns += staticfiles_urlpatterns()
