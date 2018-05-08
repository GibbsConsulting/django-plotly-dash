import dash
import dash_core_components as dcc
import dash_html_components as html

from django_plotly_dash import DelayedDash

app = DelayedDash('SimpleExample')

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
    return 'You\'ve selected "{}"'.format(dropdown_value)

a2 = DelayedDash("Ex2")
a2.layout = html.Div([
    dcc.RadioItems(id="dropdown-one",options=[{'label':i,'value':j} for i,j in [
    ("BEER","Beer"),("WIne","wine"),]
    ],value="Beer"),
    html.Div(id="output-one")
    ])

@a2.callback(
    dash.dependencies.Output('output-one','children'),
    [dash.dependencies.Input('dropdown-one','value')]
    )
def callback_c(*args,**kwargs):
    return "Args are %s and kwargs are %s" %("".join(*args),str(kwargs))

