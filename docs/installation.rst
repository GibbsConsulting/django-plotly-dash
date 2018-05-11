.. _installation:

Installation
============

Use pip to install the package, preferably to a local virtualenv.::

    pip install django_plotly_dash

Then, add ``django_plotly_dash`` to ``INSTALLED_APPS`` in the Django settings.py file::

    INSTALLED_APPS = [
        ...
        'django_plotly_dash.apps.DjangoPlotlyDashConfig',
        ...
        ]

The ``plotly_item`` tag in the ``plotly_dash`` tag library can then be used to render any registered dash component. See :ref:`simple_use` for a simple example.

The project directory name ``django_plotly_dash`` can also be used on its own if preferred, but this will then skip the use of readable application names in
the Django admin interface.

Source code and demo
--------------------

The source code repository contains a simple demo application.

To install and run it::

  git clone https://github.com/GibbsConsulting/django-plotly-dash.git

  cd django-plotly-dash

  ./make_env                # sets up a virtual environment
                            #   with direct use of the source
                            #   code for the package

  ./prepare_demo            # prepares and launches the demo
                            #   using the Django debug server
                            #   at http://localhost:8000

This will launch a simple Django application. A superuser account is also configured, with both username and password set to ``admin``.
