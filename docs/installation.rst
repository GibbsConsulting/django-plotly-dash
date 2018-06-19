.. _installation:

Installation
============

Use pip to install the package, preferably to a local virtualenv.::

    pip install django_plotly_dash

Then, add ``django_plotly_dash`` to ``INSTALLED_APPS`` in the Django ``settings.py`` file::

    INSTALLED_APPS = [
        ...
        'django_plotly_dash.apps.DjangoPlotlyDashConfig',
        ...
        ]

The project directory name ``django_plotly_dash`` can also be used on its own if preferred, but this will stop the use of readable application names in
the Django admin interface.

The application's routes need to be registered within the routing structure by an appropriate ``include`` statement in
a ``urls.py`` file::

    urlpatterns = [
        ...
        path('django_plotly_dash/', include('django_plotly_dash.urls')),
    ]

The name within the URL is not important and can be changed.

For the final installation step, a migration is needed to update the
database::

    ./manage.py migrate

The ``plotly_item`` tag in the ``plotly_dash`` tag library can then be used to render any registered dash component. See :ref:`simple_use` for a simple example.

It is important to ensure that any applications are registered using the ``DjangoDash`` class. This means that any python module containing the registration code has to be known to Django and loaded at the appropriate time. An easy way to ensure this is to import these modules into a standard Django file loaded at registration time.

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

Note that the current demo, along with the codebase, is in a prerelease and very raw form.


