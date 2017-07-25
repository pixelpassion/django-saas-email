=============================
Django Saas Email Manager
=============================

.. image:: https://badge.fury.io/py/django-saas-email.svg
    :target: https://badge.fury.io/py/django-saas-email

.. image:: https://travis-ci.org/unicorn-supplies/django-saas-email.svg?branch=master
    :target: https://travis-ci.org/unicorn-supplies/django-saas-email

.. image:: https://codecov.io/gh/unicorn-supplies/django-saas-email/branch/master/graph/badge.svg
    :target: https://codecov.io/gh/unicorn-supplies/django-saas-email

An email manager for sending emails with templates, mail history and admin.

Features
--------

* Use of `Mailhog <https://github.com/mailhog/MailHog/>`_ for local email testing.
* Send emails via `django-anymail <https://github.com/anymail/django-anymail>`_ (using `Sendgrid <https://sendgrid.com>`__ as default).
* Serving dynamic HTML E-Mail Templates, editable with `Tinymce <https://github.com/aljosa/django-tinymce>`_.
* Use of the awesome `Transactional email templates <https://github.com/mailgun/transactional-email-templates>`_ from `Mailgun <https://www.mailgun.com>`_.


Documentation
-------------

The full documentation is at https://django-saas-email.readthedocs.io.

Quickstart
----------

**Installation**

Installation with pip::

    pip install django-saas-email


Add it to your `INSTALLED_APPS`:

.. code-block:: python

    INSTALLED_APPS = (
        ...
        'django_saas_email.apps.DjangoSaasEmailConfig',
        ...
    )


**JSONField**

We are using the Postgres JSONField as default. If you installed `psycopg2`, everything should work fine.

If you are using a different database, you also need to install `jsonfield`::

    pip install jsonfield


**Adding the Sendgrid API Key to your settings**

In settings.py::

    SENDGRID_API_KEY=<....>

Other optional settings::

    DJANGO_SAAS_TEST_EMAIL_ADDRESS=youremailfortesting@example.org
    DJANGO_SAAS_FOOTER="""Follow <a href="#" style="font-family: 'Helvetica Neue',Helvetica,Arial,sans-serif; box-sizing: border-box; font-size: 12px; color: #999; text-decoration: underline; margin: 0;">@yourcompany</a> on Twitter"""

**Sending emails**

Basic example::

    from django_saas_email.utils import create_and_send_emails

    context={
        'first_name': 'John',
        'last_name': 'Doe',
    }

    create_and_send_mail(
        template_name="hello_world",
        context=context,
        to_address=john.doe@example.org
    )

This will create an email and send it with Sengrid.

You should use http://premailer.dialect.ca or django-premailer to create Inline CSS in HTML


Running Tests
-------------

Does the code actually work?::

    source <YOURVIRTUALENV>/bin/activate
    (myenv) $ pip install tox
    (myenv) $ tox

