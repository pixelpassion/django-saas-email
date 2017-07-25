# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations


def forwards_func(apps, schema_editor):
    # We get the model from the versioned app registry;
    # if we directly import it, it'll be the wrong version
    MailTemplate = apps.get_model("django_saas_email", "MailTemplate")
    db_alias = schema_editor.connection.alias

    html_template = """
    <meta itemprop="name" content="Confirm Email"
      style="font-family: 'Helvetica Neue',Helvetica,Arial,sans-serif; box-sizing: border-box; font-size: 14px; margin: 0;"/>
<table width="100%" cellpadding="0" cellspacing="0"
       style="font-family: 'Helvetica Neue',Helvetica,Arial,sans-serif; box-sizing: border-box; font-size: 14px; margin: 0;">
  <tr
    style="font-family: 'Helvetica Neue',Helvetica,Arial,sans-serif; box-sizing: border-box; font-size: 14px; margin: 0;">
    <td class="content-block"
        style="font-family: 'Helvetica Neue',Helvetica,Arial,sans-serif; box-sizing: border-box; font-size: 14px; vertical-align: top; margin: 0; padding: 0 0 20px;"
        valign="top">
      <strong>Hello {{first_name}} {{last_name}}!</strong>
    </td>
  </tr>
  <tr
    style="font-family: 'Helvetica Neue',Helvetica,Arial,sans-serif; box-sizing: border-box; font-size: 14px; margin: 0;">
    <td class="content-block"
        style="font-family: 'Helvetica Neue',Helvetica,Arial,sans-serif; box-sizing: border-box; font-size: 14px; vertical-align: top; margin: 0; padding: 0 0 20px;"
        valign="top">
      Welcome to django-saas-email :) You can change the template in the MailTemplate admin.
    </td>
  </tr>
  <tr
    style="font-family: 'Helvetica Neue',Helvetica,Arial,sans-serif; box-sizing: border-box; font-size: 14px; margin: 0;">
    <td class="content-block" itemprop="handler" itemscope itemtype="http://schema.org/HttpActionHandler"
        style="font-family: 'Helvetica Neue',Helvetica,Arial,sans-serif; box-sizing: border-box; font-size: 14px; vertical-align: top; margin: 0; padding: 0 0 20px;"
        valign="top">
      <a href="http://www.google.com" class="btn-primary" itemprop="url"
         style="font-family: 'Helvetica Neue',Helvetica,Arial,sans-serif; box-sizing: border-box; font-size: 14px; color: #FFF; text-decoration: none; line-height: 2em; font-weight: bold; text-align: center; cursor: pointer; display: inline-block; border-radius: 5px; text-transform: capitalize; background-color: #348eda; margin: 0; border-color: #348eda; border-style: solid; border-width: 10px 20px;">Go
        to google.com</a>
    </td>
  </tr>
</table>
    """

    MailTemplate.objects.using(db_alias).bulk_create([
        MailTemplate(name="hello", html_template=html_template, subject="Hello {{first_name}} {{last_name}}!"),
    ])


def reverse_func(apps, schema_editor):
    # forwards_func() creates two Country instances,
    # so reverse_func() should delete them.
    MailTemplate = apps.get_model("django_saas_email", "MailTemplate")
    db_alias = schema_editor.connection.alias
    MailTemplate.objects.using(db_alias).filter(name="hello").delete()


class Migration(migrations.Migration):

    dependencies = [
        ('django_saas_email', '0001_initial'),
    ]
    operations = [
        migrations.RunPython(forwards_func, reverse_func),
    ]
