.. _local_assets:

Local assets
============

Local ploty dash assets are integrated into the standard Django staticfiles structure. This requires additional
settings for both staticfiles finders and middleware, and also providing a list of the components used. The
specific steps are listed in the :ref:`configuration` section.

Individual applications can set a ``serve_locally`` flag but the use of the global setting in the ``PLOTLY_DASH``
variable is recommended.

Additional components
---------------------

Some components, such as ``dash-bootstrap-components``, require external packages such as Bootstrap to be supplied. In
turn this can be achieved using for example the ``bootstrap4`` Django application. As a consequence, dependencies on
external URLs are introduced.

This can be avoided by use of the ``dpd-static-support`` package, which supplies mappings to locally served versions of
these assets. Installation is through the standard ``pip`` approach

.. code-block:: bash

   pip install dpd-static-support

and then the package should be added as both an installed app and to the ``PLOTLY_COMPONENTS`` list
in ``settings.py``, along with the associated middleware

.. code-block:: python

    INSTALLED_APPS = [
        ...
        'dpd_static_support',
    ]

    MIDDLEWARE = [
        ...
        'django_plotly_dash.middleware.ExternalRedirectionMiddleware',
    ]

    PLOTLY_COMPONENTS = [
        ...
        'dpd_static_support'
    ]

Note that the middleware can be safely added even if the ``serve_locally`` functionality is not in use.

Known issues
------------

Absolute paths to assets will not work correctly. For example:

.. code-block:: python

    app.layout = html.Div([html.Img(src=localState.get_asset_url('image_one.png')),
                           html.Img(src='assets/image_two.png'),
                           html.Img(src='/assets/image_three.png'),
                           ])

Of these three images, both ``image_one.png`` and ``image_two.png`` will be served up - through the static files
infrastructure - from the ``assets`` subdirectory relative to the code defining the ``app`` object. However, when
rendered the application will attempt to load ``image_three.png`` using an absolute path. This is unlikely to
be the desired result, but does permit the use of absolute URLs within the server.

