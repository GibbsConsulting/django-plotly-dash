.. _template_tags:

Template tags
=============

Template tags are provided in the ``plotly_dash`` library:

.. code-block:: jinja

  {%load plotly_dash%}

The ``plotly_app`` template tag
-------------------------------

Importing the ``plotly_dash`` library provides the ``plotly_app`` template tag:

.. code-block:: jinja

  {%load plotly_dash%}

  {%plotly_app name="SimpleExample"%}

This tag inserts
a ``DjangoDash`` app within a page as a responsive ``iframe`` element.

The tag arguments are:

:name = None: The name of the application, as passed to a ``DjangoDash`` constructor.
:slug = None: The slug of an existing ``DashApp`` instance.
:da = None: An existing ``django_plotly_dash.models.DashApp`` model instance.
:ratio = 0.1: The ratio of height to width. The container will inherit its width as 100% of its parent, and then rely on
              this ratio to set its height.
:use_frameborder = "0": HTML element property of the iframe containing the application.

At least one of ``da``, ``slug`` or ``name`` must be provided. An object identified by ``slug`` will always be used, otherwise any
identified by ``name`` will be. If either of these arguments are provided, they must resolve to valid objects even if
not used. If neither are provided, then the model instance in ``da`` will be used.

The ``plotly_message_pipe`` template tag
----------------------------------------

This template tag has to be inserted on every page that uses live updating:

.. code-block:: jinja

  {%load plotly_dash%}

  {%plotly_app ... DjangoDash instances using live updating ... %}

  {%plotly_message_pipe%}

The tag inserts javascript needed for the :ref:`Pipe <pipe_component>` component to operate. It can be inserted anywhere
on the page, and its ordering relative to the ``Dash`` instances using updating is not important, so placing it in
the page footer - to avoid delaying the main page load - along
with other scripts is generally advisable.

The ``plotly_app_identifier`` template tag
-----------------------------------------

This tag provides an identifier for an app, in a form that is suitable for use as a classname or identifier
in HTML:

.. code-block:: jinja

  {%load plotly_dash%}

  {%plotly_app_identifier name="SimpleExample"%}

  {%plotly_app_identifier slug="liveoutput-2" postfix="A"%}

The identifier, if the tag is not passed a ``slug``, is the result of passing the identifier of the app through
the ``django.utils.text.slugify`` function.

The tag arguments are:

:name = None: The name of the application, as passed to a ``DjangoDash`` constructor.
:slug = None: The slug of an existing ``DashApp`` instance.
:da = None: An existing ``django_plotly_dash.models.DashApp`` model instance.
:postfix = None: An optional string; if specified it is appended to the identifier with a hyphen.

The validity rules for these arguments are the same as those for the ``plotly_app`` template tag. If
supplied, the ``postfix`` argument
should already be in a slug-friendly form, as no processing is performed on it.

The ``plotly_class`` template tag
-----------------------------------------

Generate a string of class names, suitable for a ``div`` or other element that wraps around ``django-plotly-dash`` template content.

.. code-block:: jinja

  {%load plotly_dash%}

  <div class="{%plotly_class slug="liveoutput-2" postfix="A"%}">
    {%plotly_app slug="liveoutput-2" ratio="0.5" %}
  </div>

The identifier, if the tag is not passed a ``slug``, is the result of passing the identifier of the app through
the ``django.utils.text.slugify`` function.

The tag arguments are:

:name = None: The name of the application, as passed to a ``DjangoDash`` constructor.
:slug = None: The slug of an existing ``DashApp`` instance.
:da = None: An existing ``django_plotly_dash.models.DashApp`` model instance.
:prefix = None: Optional prefix to use in place of the text ``django-plotly-dash`` in each class name
:postfix = None: An optional string; if specified it is appended to the app-specific identifier with a hyphen.
:template_type = None: Optional text to use in place of ``iframe`` in the template-specific class name

The tag inserts a string with three class names in it. One is just the ``prefix`` argument, one
has the ``template_type`` appended, and the final one has the app identifier (as generated
by the ``plotly_app_identifier`` tag) and any ``postfix`` appended.

The validity rules for these arguments are the same as those for the ``plotly_app``  and ``plotly_app_identifier`` template tags. Note
that none of the ``prefix``, ``postfix`` and ``template_type`` arguments are modified and they should
already be in a slug-friendly form, or otherwise fit for their intended purpose.
