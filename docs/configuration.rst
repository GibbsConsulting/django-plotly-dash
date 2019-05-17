.. _configuration:

Configuration options
=====================

The ``PLOTLY_DASH`` settings variable is used for configuring ``django-plotly-dash``. Default values are shown
below.

.. code-block:: python

  PLOTLY_DASH = {

      # Route used for the message pipe websocket connection
      "ws_route" :   "dpd/ws/channel",

      # Route used for direct http insertion of pipe messages
      "http_route" : "dpd/views",

      # Flag controlling existince of http poke endpoint
      "http_poke_enabled" : True,

      # Insert data for the demo when migrating
      "insert_demo_migrations" : False,

      # Timeout for caching of initial arguments in seconds
      "cache_timeout_initial_arguments": 60,

      # Name of view wrapping function
      "view_decorator": None,

      # Flag to control location of initial argument storage
      "cache_arguments": True,

      # Flag controlling local serving of assets
      "serve_locally': False,
  }

Defaults are inserted for missing values. It is also permissible to not have any ``PLOTLY_DASH`` entry in
the Django settings file.

The Django staticfiles infrastructure is used to serve all local static files for
the Dash apps. This requires adding a setting for the specification of additional static
file finders

.. code-block:: python

  # Staticfiles finders for locating dash app assets and related files

  STATICFILES_FINDERS = [

      'django.contrib.staticfiles.finders.FileSystemFinder',
      'django.contrib.staticfiles.finders.AppDirectoriesFinder',

      'django_plotly_dash.finders.DashAssetFinder',
      'django_plotly_dash.finders.DashComponentFinder',
      'django_plotly_dash.finders.DashAppDirectoryFinder',
  ]

and also providing a list of components used

.. code-block:: python

  # Plotly components containing static content that should
  # be handled by the Django staticfiles infrastructure

  PLOTLY_COMPONENTS = [

      # Common components
      'dash_core_components',
      'dash_html_components',
      'dash_renderer',

      # django-plotly-dash components
      'dpd_components',
      # static support if serving local assets
      'dpd_static_support',

      # Other components, as needed
      'dash_bootstrap_components',
  ]

This list should be extended with any additional components that the applications
use, where the components have files that have to be served locally.

Furthermore, middleware should be added for redirection of external assets from
underlying packages, such as ``dash-bootstrap-components``. With the standard
Django middleware, along with ``whitenoise``, the entry within the ``settings.py``
file will look something like

.. code-block:: python

  # Standard Django middleware with the addition of both
  # whitenoise and django_plotly_dash items

  MIDDLEWARE = [

        'django.middleware.security.SecurityMiddleware',

        'whitenoise.middleware.WhiteNoiseMiddleware',

        'django.contrib.sessions.middleware.SessionMiddleware',
        'django.middleware.common.CommonMiddleware',
        'django.middleware.csrf.CsrfViewMiddleware',
        'django.contrib.auth.middleware.AuthenticationMiddleware',
        'django.contrib.messages.middleware.MessageMiddleware',

        'django_plotly_dash.middleware.BaseMiddleware',
        'django_plotly_dash.middleware.ExternalRedirectionMiddleware',

        'django.middleware.clickjacking.XFrameOptionsMiddleware',
    ]


Individual apps can set their ``serve_locally`` flag. However, it is recommended to use
the equivalent global ``PLOTLY_DASH`` setting to provide a common approach for all
static assets. See :ref:`local_assets` for more information on how local assets are configured
and served as part of the standard Django staticfiles approach, along with details on the
integration of other components and some known issues.

.. _endpoints:

Endpoints
---------

The websocket and direct http message endpoints are separately configurable. The configuration options exist to satisfy
two requirements

  * Isolate paths that require serving with ASGI. This allows the asynchronous routes - essentially the websocket connections
    and any other ones from the rest of the application - to be served using ``daphne`` or similar, and the bulk of the
    (synchronous) routes to be served using a WSGI server such as ``gunicorn``.
  * Isolate direct http posting of messages to restrict their use. The motivation behind this http endpoint is to provide
    a private service that allows other
    parts of the overall application to send notifications to ``Dash`` applications, rather than expose this functionality
    as part of the public API.

A reverse proxy front end, such as ``nginx``, can route appropriately according to URL.

.. _view_decoration:

View decoration
---------------

Each view delegated through to ``plotly_dash`` can be wrapped using a view decoration function. This enables access to be restricted to
logged-in users, or using a desired conditions based on the user and session state.

To restrict all access to logged-in users, use the ``login_required`` wrapper:

.. code-block:: python

  PLOTLY_DASH = {

      ...
      # Name of view wrapping function
      "view_decorator": "django_plotly_dash.access.login_required",
      ...
  }

More information can be found in the :ref:`view decoration <access_control>` section.

.. _cache_arguments:

Initial arguments
-----------------

Initial arguments are stored within the server between the specification of an app in a template tag and the invocation of the
view functions for the app. This storage is transient and can be efficiently performed using Django's caching framework. In some
situations, however, a suitably configured cache is not available. For this use case, setting the ``cache_arguments`` flag to ``False`` will
cause initial arguments to be placed inside the Django session.
