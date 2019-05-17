.. _faq:

FAQ
===

* What environment versions are supported?

At least v3.5 of Python, and v2.0 of Django, are needed.

* Is a ``virtualenv`` mandatory?

No, but it is strongly recommended for any Python work.

* What about Windows?

The python package should work anywhere that Python does. Related applications, such as Redis, have their
own requirements but are accessed using standard network protocols.

* How do I report a bug or other issue?

Create a `github issue <https://github.com/GibbsConsulting/django-plotly-dash/issues>`_. See :ref:`bug reporting <bug-reporting>` for details
on what makes a good bug report.

* Where should ``Dash`` layout and callback functions be placed?

In general, the only constraint on the files containing these functions is that they should be imported into the file containing
the ``DjangoDash`` instantiation. This is discussed in
the :ref:`installation` section and also
in this github `issue <https://github.com/GibbsConsulting/django-plotly-dash/issues/58>`_.

* Can per-user or other fine-grained access control be used?

 Yes. See the :ref:`view_decoration` configuration setting and :ref:`access_control` section.

* What settings are needed to run the server in debug mode?

The ``prepare_demo`` script in the root of the git repository contains the full set of commands
for running the server in debug mode. In particular, the debug server is launched with the ``--nostatic`` option. This
will cause the staticfiles to be served from the collected files in the ``STATIC_ROOT`` location rather than the normal
``runserver`` behaviour of serving directly from the various
locations in the ``STATICFILES_DIRS`` list.

* Is use of the ``get_asset_url`` function optional for including static assets?

No, it is needed. Consider this example (it is part of ``demo-nine``):

.. code-block:: python

  localState = DjangoDash("LocalState",
                          serve_locally=True)

  localState.layout = html.Div([html.Img(src=localState.get_asset_url('image_one.png')),
                                html.Img(src='/assets/image_two.png'),
                                ])

The first ``Img`` will have its source file correctly served up by Django as a standard static file. However, the second image will
not be rendered as the path will be incorrect.

See the :ref:`local_assets` section for more information on configuration with local assets.

* Is there a live demo available?

Yes. It can be found `here <https://djangoplotlydash.com>`_
