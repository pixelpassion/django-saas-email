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

* Use of [Mailhog](#) for local email testing
* Send emails via [Anymail](#) (using [Sendgrid](#) as default)
* Serving dynamic HTML E-Mail Templates, editable with [Tinymce](#)
* Use of the [Transactional email templates](https://github.com/mailgun/transactional-email-templates) from [Mailgun](https://www.mailgun.com).


Documentation
-------------

The full documentation is at https://django-saas-email.readthedocs.io.

Quickstart
----------

Install Django Saas Email Manager::

    pip install django-saas-email


Add it to your `INSTALLED_APPS`:

.. code-block:: python

    INSTALLED_APPS = (
        ...
        'django_saas_email.apps.DjangoSaasEmailConfig',
        ...
    )


We are using the Postgres JSONField as default. If you installed `psycopg2`, everything should work fine.

If you are using a different database, you also need to install `jsonfield`::

    pip install jsonfield


Sending emails::

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



Running Tests
-------------

Does the code actually work?

::

    source <YOURVIRTUALENV>/bin/activate
    (myenv) $ pip install tox
    (myenv) $ tox

Credits
-------

Tools used in rendering this package:

*  Cookiecutter_
*  `cookiecutter-djangopackage`_

.. _Cookiecutter: https://github.com/audreyr/cookiecutter
.. _`cookiecutter-djangopackage`: https://github.com/pydanny/cookiecutter-djangopackage
