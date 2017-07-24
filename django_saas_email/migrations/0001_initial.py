# -*- coding: utf-8 -*-
# Generated by Django 1.11.3 on 2017-07-24 16:57
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone
import jsonfield.fields
import tinymce.models
import uuid


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Mail',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False, unique=True, verbose_name='ID')),
                ('from_address', models.EmailField(help_text="The 'from' field of the email", max_length=254, verbose_name='Sender email address')),
                ('to_address', models.EmailField(help_text="The 'to' field of the email", max_length=254, verbose_name='Recipient email address')),
                ('delivery_mail_id', models.IntegerField(blank=True, editable=False, help_text='The ID is saved after correct sending', null=True, verbose_name='Unique mail sender ID')),
                ('delivery_status', models.IntegerField(blank=True, editable=False, help_text='The Mail sender status', null=True, verbose_name='Status of Mail sender')),
                ('subject', models.CharField(blank=True, help_text='Subject line for a mail', max_length=500, null=True, verbose_name='Email Subject line')),
                ('context', jsonfield.fields.JSONField(help_text='JSON dump of context dictionary used to fill in templates', verbose_name='Data of email context')),
                ('time_created', models.DateTimeField(default=django.utils.timezone.now, editable=False, help_text='When was the mail created?', verbose_name='Creation time')),
                ('time_sent', models.DateTimeField(blank=True, editable=False, help_text='When was the mail send via the backend?', null=True, verbose_name='Sent time')),
                ('time_delivered', models.DateTimeField(blank=True, editable=False, help_text='Actual delivery time by the email backend', null=True, verbose_name='Delivery time')),
                ('used_backend', models.CharField(blank=True, editable=False, help_text='Which email backend was used for sending?', max_length=128, null=True, verbose_name='E-Mail Backend')),
            ],
        ),
        migrations.CreateModel(
            name='MailManager',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
            ],
        ),
        migrations.CreateModel(
            name='MailTemplate',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(help_text='Template name; a short all-lowercase string', max_length=100, unique=True, verbose_name='Template name')),
                ('subject', models.CharField(help_text='A format string like "Hello {}"; required', max_length=200, verbose_name='Email subject line template')),
                ('html_template', tinymce.models.HTMLField(help_text="The HTML template, written with Django's template syntax; required", verbose_name='HTML template (required)')),
                ('text_template', models.TextField(blank=True, default='', help_text='This is an optional field for adding a custom text-only version of this template. If left blank, the plaintext email will be generated dynamically from the HTML when needed.', null=True, verbose_name='Text template (optional)')),
            ],
        ),
        migrations.AddField(
            model_name='mail',
            name='template',
            field=models.ForeignKey(help_text='The used template', on_delete=django.db.models.deletion.CASCADE, to='django_saas_email.MailTemplate', verbose_name='Used Mail template'),
        ),
    ]
