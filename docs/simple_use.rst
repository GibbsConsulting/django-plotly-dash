.. _simple_use:

Simple usage
============

To use existing dash applications, first register them using the ``DjangoDash`` class. This
replaces the ``Dash`` class from the ``dash`` package.

Taking a simple example inspired by the excellent `getting started <https://dash.plot.ly/getting-started-part-2>`_ guide:

.. code-block:: python

  import dash
  import dash_core_components as dcc
  import dash_html_components as html

  from django_plotly_dash import DjangoDash

  app = DjangoDash('SimpleExample')   # replaces dash.Dash

  app.layout = html.Div([
      dcc.RadioItems(
          id='dropdown-color',
          options=[{'label': c, 'value': c.lower()} for c in ['Red', 'Green', 'Blue']],
          value='red'
      ),
      html.Div(id='output-color'),
      dcc.RadioItems(
          id='dropdown-size',
          options=[{'label': i,
                    'value': j} for i, j in [('L','large'), ('M','medium'), ('S','small')]],
          value='medium'
      ),
      html.Div(id='output-size')

  ])

  @app.callback(
      dash.dependencies.Output('output-color', 'children'),
      [dash.dependencies.Input('dropdown-color', 'value')])
  def callback_color(dropdown_value):
      return "The selected color is %s." % dropdown_value

  @app.callback(
      dash.dependencies.Output('output-size', 'children'),
      [dash.dependencies.Input('dropdown-color', 'value'),
       dash.dependencies.Input('dropdown-size', 'value')])
  def callback_size(dropdown_color, dropdown_size):
      return "The chosen T-shirt is a %s %s one." %(dropdown_size,
                                                    dropdown_color)

Note that the ``DjangoDash`` constructor requires a name to be specified. This name is then used to identify the dash app
in :ref:`templates <template_tags>`:

.. code-block:: jinja

  {%load plotly_dash%}

  {%plotly_app name="SimpleExample"%}

Direct use in this manner, without any application state or
use of live updating, is equivalent to inserting an ``iframe`` containing the
URL of a ``Dash`` application.

.. note::
  The registration code needs to be in a location
  that will be imported into the Django process before any model or
  template tag attempts to use it. The example Django application
  in the demo subdirectory achieves this through an import in the main ``urls.py`` file, 
  but any ``views.py`` would also be sufficient.

