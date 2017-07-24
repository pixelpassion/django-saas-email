=====
Usage
=====

To use Django Saas Email Manager in a project, add it to your `INSTALLED_APPS`:

.. code-block:: python

    INSTALLED_APPS = (
        ...
        'django_saas_email.apps.DjangoSaasEmailConfig',
        ...
    )

Add Django Saas Email Manager's URL patterns:

.. code-block:: python

    from django_saas_email import urls as django_saas_email_urls


    urlpatterns = [
        ...
        url(r'^', include(django_saas_email_urls)),
        ...
    ]
