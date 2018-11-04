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
  }

Defaults are inserted for missing values. It is also permissible to not have any ``PLOTLY_DASH`` entry in
the Django settings file.

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
