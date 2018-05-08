.. _simple_use:

Simple Usage
============

To use existing dash applications, first register them using the ``DelayedDash`` class. This
replaces the ``dash.Dash`` class of ``plotly.py``

Taking as an example a slightly modified variant of one of the `getting started <https://dash.plot.ly/getting-started-part-2>`_ examples::

  import dash
  import dash_core_components as dcc
  import dash_html_components as html

  from django_plotly_dash import DelayedDash

  app = DelayedDash('SimpleExample')   # replaces dash.Dash

  app.layout = html.Div([
      dcc.RadioItems(
          id='dropdown-a',
          options=[{'label': i, 'value': i} for i in ['Canada', 'USA', 'Mexico']],
          value='Canada'
      ),
      html.Div(id='output-a'),

      dcc.RadioItems(
          id='dropdown-b',
          options=[{'label': i, 'value': i} for i in ['MTL', 'NYC', 'SF']],
          value='MTL'
      ),
      html.Div(id='output-b')

  ])

  @app.callback(
      dash.dependencies.Output('output-a', 'children'),
      [dash.dependencies.Input('dropdown-a', 'value')])
  def callback_a(dropdown_value):
      return 'You\'ve selected "{}"'.format(dropdown_value)


  @app.callback(
      dash.dependencies.Output('output-b', 'children'),
      [dash.dependencies.Input('dropdown-a', 'value'),
       dash.dependencies.Input('dropdown-b', 'value')])
  def callback_b(dropdown_value,other_dd):
      return 'You\'ve selected "{}" and "{}"'.format(dropdown_value,
                                                     other_dd)

Note that the ``DelayedDash`` constructor requires a name to be specified. This name is then used to identify the dash app in
templates:::

  {%load plotly_dash%}

  {%plotly_item "SimpleExample"%}

Note that the registration code needs to be in a location
that will be imported into the Django process before any template tag attempts to use it. The example Django application
in the demo subdirectory achieves this through an import in the main urls.py file; any views.py would also be sufficient.

