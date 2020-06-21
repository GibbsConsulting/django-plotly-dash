.. _bootstrap:

Using Bootstrap
===============

The ``django-plotly-dash`` package is frequently used with the ``dash-bootstrap-components`` package, and this
requires a number of steps to set up correctly.

This section is
a checkist of the required confiuration steps.

- install the package as descrbed in the :ref:`installation <installation>` section

- install the static support package with ``pip install dpd-static-support``

- add the various settings in the :ref:`configuration <configuration>` section, particularly
  the STATICFILES_FINDERS, PLOTLY_COMPONENTS and MIDDLEWARE ones.

- install django-bootstrap 4 with ``pip install django-bootstrap4`` and add ``bootstrap4`` to INSTALLED_APPS in the
  project's ``settings.py`` file

- make sure that the settings for serving static files are set correctly, particularly STATIC_ROOT, as
  described in the Django `documentation <https://docs.djangoproject.com/en/3.0/howto/static-files/>`_

- use the ``prepare_demo`` script or perform the equivalent steps, paricularly the ``migrate`` and ``collectstatic`` steps

- make sure ``add_bootstrap_links=True`` is set for apps using ``dash-bootstrap-components``

- the Django documentation `deployment <https://docs.djangoproject.com/en/3.0/howto/static-files/deployment/>`_ section
  covers setting up the serving of static files for production
