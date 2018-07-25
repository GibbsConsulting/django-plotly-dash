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

