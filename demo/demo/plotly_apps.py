import dash
import dash_core_components as dcc
import dash_html_components as html

import dpd_components as dpd

from django_plotly_dash import DjangoDash

app = DjangoDash('SimpleExample')

app.layout = html.Div([
    dcc.RadioItems(
        id='dropdown-color',
        options=[{'label': c, 'value': c.lower()} for c in ['Red', 'Green', 'Blue']],
        value='red'
    ),
    html.Div(id='output-color'),
    dcc.RadioItems(
        id='dropdown-size',
        options=[{'label': i, 'value': j} for i, j in [('L','large'), ('M','medium'), ('S','small')]],
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

a2 = DjangoDash("Ex2")
a2.layout = html.Div([
    dcc.RadioItems(id="dropdown-one",options=[{'label':i,'value':j} for i,j in [
    ("O2","Oxygen"),("N2","Nitrogen"),("CO2","Carbon Dioxide")]
    ],value="Oxygen"),
    html.Div(id="output-one")
    ])

@a2.expanded_callback(
    dash.dependencies.Output('output-one','children'),
    [dash.dependencies.Input('dropdown-one','value')]
    )
def callback_c(*args,**kwargs):
    da = kwargs['dash_app']
    return "Args are [%s] and kwargs are %s" %(",".join(args),str(kwargs))

a3 = DjangoDash("Connected")

a3.layout = html.Div([
    dpd.Pipe(id="dynamic",
             value="Dynamo 123",
             label="rotational energy",
             channel_name="test_widget_channel",
             uid="need_to_generate_this"),
    dpd.DPDirectComponent(id="direct"),
    dcc.RadioItems(id="dropdown-one",options=[{'label':i,'value':j} for i,j in [
    ("O2","Oxygen"),("N2","Nitrogen"),("CO2","Carbon Dioxide")]
    ],value="Oxygen"),
    html.Div(id="output-three")
    ])

@a3.expanded_callback(
    dash.dependencies.Output('output-three','children'),
    [dash.dependencies.Input('dynamic','value'),
     dash.dependencies.Input('dynamic','label'),
     ])
def callback_a3(*args, **kwargs):
    da = kwargs['dash_app']
    return "Args are [%s] and kwargs are %s" %(",".join(args),str(kwargs))
