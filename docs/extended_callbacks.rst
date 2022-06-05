.. _extended_callbacks:

Extended callback syntax
========================

The ``DjangoDash`` class allows callbacks to request extra arguments when registered.

To do this, simply add to your callback function the extra arguments you would like to receive
after the usual parameters for your ``Input`` and ``State``.
This will cause these callbacks registered with this application to receive extra parameters
in addition to their usual callback parameters.

If you specify a ``kwargs`` in your callback, it will receive all possible extra parameters (see below for a list).
If you specify explicitly extra parameters from the list below, only these will be passed to your callback.

For example, the ``plotly_apps.py`` example contains this dash application:

.. code-block:: python

  import dash
  from dash import dcc, html

  from django_plotly_dash import DjangoDash

  a2 = DjangoDash("Ex2")

  a2.layout = html.Div([
      dcc.RadioItems(id="dropdown-one",options=[{'label':i,'value':j} for i,j in [
      ("O2","Oxygen"),("N2","Nitrogen"),("CO2","Carbon Dioxide")]
      ],value="Oxygen"),
      html.Div(id="output-one")
      ])

  @a2.callback(
      dash.dependencies.Output('output-one','children'),
      [dash.dependencies.Input('dropdown-one','value')]
      )
  def callback_c(*args,**kwargs):
      da = kwargs['dash_app']
      return "Args are [%s] and kwargs are %s" %(",".join(args), kwargs)

The additional arguments, which are reported as the ``kwargs`` content in this example, include

:callback_context: The ``Dash`` callback context. See the `documentation <https://dash.plotly.com/advanced-callbacks`_ on the content of
                   this variable. This variable is provided as an argument to the callback as well as
                   the ``dash.callback_context`` global variable.
:dash_app: For stateful applications, the ``DashApp`` model instance
:dash_app_id: The application identifier. For stateless applications, this is the (slugified) name given to the ``DjangoDash`` constructor.
              For stateful applications, it is the (slugified) unique identifier for the associated model instance.
:request: The Django request object.
:session_state: A dictionary of information, unique to this user session. Any changes made to its content during the
                callback are persisted as part of the Django session framework.
:user: The Django User instance.

Possible alternatives to ``kwargs``

.. code-block:: python

  @a2.callback(
      dash.dependencies.Output('output-one','children'),
      [dash.dependencies.Input('dropdown-one','value')]
      )
  def callback_c(*args, dash_app):
      return "Args are [%s] and the extra parameter dash_app is %s" %(",".join(args), dash_app)

  @a2.callback(
      dash.dependencies.Output('output-one','children'),
      [dash.dependencies.Input('dropdown-one','value')]
      )
  def callback_c(*args, dash_app, **kwargs):
      return "Args are [%s], the extra parameter dash_app is %s and kwargs are %s" %(",".join(args), dash_app, kwargs)


The ``DashApp`` model instance can also be configured to persist itself on any change. This is discussed
in the :ref:`models_and_state` section.

The ``callback_context`` argument is provided in addition to the ``dash.callback_context`` global variable. As a rule, the use of
global variables should generally be avoided. The context provided by ``django-plotly-dash`` is not the same as the one
provided by the underlying ``Dash`` library, although its property values are the same and code that uses the content of this
variable should work unchanged. The use of
this global variable in any asychronous or multithreaded application is not
supported, and the use of the callback argument is strongly recommended for all use cases.


.. _using_session_state:
Using session state
-------------------

The :ref:`walkthrough <session_example>` of the session state example details how
the XXX demo interacts with a ``Django`` session.

Unless an explicit pipe is created, changes to the session state and other server-side objects are not automatically
propagated to an application. Something in the front-end UI has to invoke a callback; at this point the
latest version of these objects will be provided to the callback. The same considerations
as in other Dash `live updates <https://dash.plot.ly/live-updates>`_ apply.

The :ref:`live updating <updating>` section discusses how ``django-plotly-dash`` provides
an explicit pipe that directly enables the updating of applications.
