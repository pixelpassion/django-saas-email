# Generated by Django 2.1.2 on 2018-10-16 23:27

import django.db.models.deletion
import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("django_saas_email", "0002_add_hello_template"),
    ]

    operations = [
        migrations.CreateModel(
            name="Attachment",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("name", models.CharField(max_length=100)),
                ("attached_file", models.FileField(upload_to="email-attachments")),
                (
                    "time_created",
                    models.DateTimeField(
                        default=django.utils.timezone.now,
                        editable=False,
                        verbose_name="Creation time",
                    ),
                ),
            ],
            options={
                "verbose_name": "attachment",
                "verbose_name_plural": "attachments",
                "abstract": False,
            },
        ),
        migrations.CreateModel(
            name="TemplateAttachment",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "attachment",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="templates",
                        to="django_saas_email.Attachment",
                    ),
                ),
                (
                    "template",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="attachments",
                        to="django_saas_email.MailTemplate",
                    ),
                ),
            ],
            options={
                "verbose_name": "Preselected attachment",
                "verbose_name_plural": "Preselected attachments",
            },
        ),
        migrations.AddField(
            model_name="mail",
            name="text",
            field=models.TextField(
                blank=True, null=True, verbose_name="Message text (plain)"
            ),
        ),
        migrations.AlterField(
            model_name="mail",
            name="template",
            field=models.ForeignKey(
                blank=True,
                help_text="The used template",
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                to="django_saas_email.MailTemplate",
                verbose_name="Used Mail template",
            ),
        ),
        migrations.AddField(
            model_name="mail",
            name="selected_attachments",
            field=models.ManyToManyField(blank=True, to="django_saas_email.Attachment"),
        ),
        migrations.AddField(
            model_name="mailtemplate",
            name="preselected_attachments",
            field=models.ManyToManyField(
                blank=True,
                through="django_saas_email.TemplateAttachment",
                to="django_saas_email.Attachment",
            ),
        ),
    ]
