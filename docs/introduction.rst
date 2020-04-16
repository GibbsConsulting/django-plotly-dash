.. _introduction:

Introduction
============

The purpose of ``django-plotly-dash`` is to enable `Plotly Dash <https://dash.plot.ly>`_ applications
to be served up as part of a `Django <https://www.djangoproject.com/>`_ application, in order to provide
these features:

* Multiple dash applications can be used on a single page
* Separate instances of a dash application can persist along with internal state
* Leverage user management and access control and other parts of the Django infrastructure
* Consolidate into a single server process to simplify scaling

There is nothing here that cannot be achieved through expanding the Flask app around Plotly Dash, or indeed by using an alternative web
framework. The purpose of this project is to enable the above features, given that the choice to use Django has already been made.

The source code can be found in `this github repository <https://github.com/GibbsConsulting/django-plotly-dash>`_. This repository also includes
a self-contained demo application, which can also be viewed `online <https://djangoplotlydash.com>`_.

.. _overview:

Overview
--------

``django_plotly_dash`` works by wrapping around the ``dash.Dash`` object. The http endpoints exposed by the
``Dash`` application are mapped to Django ones, and an application is embedded into a webpage through the
use of a template tag. Multiple ``Dash`` applications can be used in a single page.

A subset of the internal state of a ``Dash`` application can be persisted as a standard Django model instance, and the application with this
internal state is then available at its own URL. This can then be embedded into one or more pages in the same manner as described
above for stateless applications.

Also, an enhanced version of the ``Dash`` callback is provided, giving the callback access to the current User, the current session, and also
the model instance associated with the application's internal state.

This package is compatible with version 2.0 onwards of Django. Use of the :ref:`live updating <updating>` feature requires
the Django Channels extension; in turn this requires a suitable messaging backend such as Redis.

