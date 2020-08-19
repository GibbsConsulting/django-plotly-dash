.. _installation:

Installation
============

The package requires version 2.2 or greater of Django, and a minimum Python version needed of 3.5.

Use ``pip`` to install the package, preferably to a local ``virtualenv``::

    pip install django_plotly_dash

Then, add ``django_plotly_dash`` to ``INSTALLED_APPS`` in the Django ``settings.py`` file::

    INSTALLED_APPS = [
        ...
        'django_plotly_dash.apps.DjangoPlotlyDashConfig',
        ...
        ]

The project directory name ``django_plotly_dash`` can also be used on its own if preferred, but this will stop the use of readable application names in
the Django admin interface.

Also, enable the use of frames within HTML documents by also adding to the ``settings.py`` file::

    X_FRAME_OPTIONS = 'SAMEORIGIN'


Further, if the :ref:`header and footer <plotly_header_footer>` tags are in use
then ``django_plotly_dash.middleware.BaseMiddleware`` should be added to ``MIDDLEWARE`` in the same file. This
can be safely added now even if not used.

If assets are being served locally through the use of the global ``serve_locally`` or on a per-app basis, then
``django_plotly_dash.middleware.ExternalRedirectionMiddleware`` should be added, along with the ``whitenoise`` package whose
middleware should also be added as per the instructions for that package. In addition, ``dpd_static_support`` should be
added to the ``INSTALLED_APPS`` setting.

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

The ``plotly_app`` tag in the ``plotly_dash`` tag library can then be used to render any registered dash component. See :ref:`simple_use` for a simple example.

It is important to ensure that any applications are registered using the ``DjangoDash`` class. This means that any python module containing the registration code has to be known to Django and loaded at the appropriate time. An easy way to ensure this is to import these modules into a standard Django file loaded at registration time.

Extra steps for live state
--------------------------

The live updating of application state uses the Django `Channels <https://channels.readthedocs.io/en/latest/index.html>`_ project and a suitable
message-passing backend. The included demonstration uses ``Redis``::

    pip install channels daphne redis django-redis channels-redis

A standard installation of the Redis package is required. Assuming the use of ``docker`` and the current production version::

    docker pull redis:4
    docker run -p 6379:6379 -d redis

The ``prepare_redis`` script in the root of the repository performs these steps.

This will launch a container running on the localhost. Following the channels documentation, as
well as adding ``channels`` to the ``INSTALLED_APPS`` list, a ``CHANNEL_LAYERS`` entry in
``settings.py`` is also needed::

    INSTALLED_APPS = [
        ...
        'django_plotly_dash.apps.DjangoPlotlyDashConfig',
        'channels',
        ...
        ]

    CHANNEL_LAYERS = {
        'default': {
            'BACKEND': 'channels_redis.core.RedisChannelLayer',
            'CONFIG': {
                'hosts': [('127.0.0.1', 6379),],
            },
        },
    }

The host and port entries in ``hosts`` should be adjusted to match the network location of the Redis instance.

Further configuration
---------------------

Further configuration options can be specified through the optional ``PLOTLY_DASH`` settings variable. The
available options are detailed in the :ref:`configuration <configuration>` section.

This includes arranging for Dash assets to be served using the Django ``staticfiles`` functionality.

A checklist for using ``dash-bootstrap-components`` can be found
in the :ref:`bootstrap <bootstrap>` section.

Source code and demo
--------------------

The source code repository contains a :ref:`simple demo <demo_notes>` application.

To install and run it::

  git clone https://github.com/GibbsConsulting/django-plotly-dash.git

  cd django-plotly-dash

  ./make_env                # sets up a virtual environment
                            #   with direct use of the source
                            #   code for the package

  ./prepare_redis           # downloads a redis docker container
                            #   and launches it with default settings
                            #   *THIS STEP IS OPTIONAL*

  ./prepare_demo            # prepares and launches the demo
                            #   using the Django debug server
                            #   at http://localhost:8000

This will launch a simple Django application. A superuser account is also configured, with both username and password set to ``admin``. If
the ``prepare_redis`` step is skipped then the fourth demo page, exhibiting live updating, will not work.

More details on setting up a development environment, which is also sufficient for running
the demo, can be found in the :ref:`development <development>` section.

Note that the current demo, along with the codebase, is in a prerelease and very raw form. An
overview can be found in the  :ref:`demonstration application<demo_notes>` section.`

