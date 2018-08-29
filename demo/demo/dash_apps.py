'''Dash demonstration application

TODO attribution here
'''

# The linter doesn't like the members of the html and dcc imports (as they are dynamic?)
#pylint: disable=no-member

import dash
import dash_core_components as dcc
import dash_html_components as html
import plotly.graph_objs as go
#import dpd_components as dpd
import numpy as np
from django_plotly_dash import DjangoDash

#from .urls import app_name
app_name = "DPD demo application"

dashboard_name1 = 'dash_example_1'
dash_example1 = DjangoDash(name=dashboard_name1,
                           serve_locally=True,
                           app_name=app_name
                          )

# Below is a random Dash app.
# I encountered no major problems in using Dash this way. I did encounter problems but it was because
# I was using e.g. Bootstrap inconsistenyly across the dash layout. Staying consistent worked fine for me.
dash_example1.layout = html.Div(id='main',
                                children=[
                                    html.Div([dcc.Dropdown(id='my-dropdown1',
                                                           options=[{'label': 'New York City', 'value': 'NYC'},
                                                                    {'label': 'Montreal', 'value': 'MTL'},
                                                                    {'label': 'San Francisco', 'value': 'SF'}
                                                                   ],
                                                           value='NYC',
                                                           className='col-md-12',
                                                          ),
                                              html.Div(id='test-output-div')
                                             ]),

                                    dcc.Dropdown(
                                        id='my-dropdown2',
                                        options=[
                                            {'label': 'Oranges', 'value': 'Oranges'},
                                            {'label': 'Plums', 'value': 'Plums'},
                                            {'label': 'Peaches', 'value': 'Peaches'}
                                        ],
                                        value='Oranges',
                                        className='col-md-12',
                                    ),

                                    html.Div(id='test-output-div2')

                                    ]) # end of 'main'

@dash_example1.expanded_callback(
    dash.dependencies.Output('test-output-div', 'children'),
    [dash.dependencies.Input('my-dropdown1', 'value')])
def callback_test(*args, **kwargs): #pylint: disable=unused-argument
    'Callback to generate test data on each change of the dropdown'

    # Creating a random Graph from a Plotly example:
    N = 500
    random_x = np.linspace(0, 1, N)
    random_y = np.random.randn(N)

    # Create a trace
    trace = go.Scatter(x=random_x,
                       y=random_y)

    data = [trace]

    layout = dict(title='',
                  yaxis=dict(zeroline=False, title='Total Expense (£)',),
                  xaxis=dict(zeroline=False, title='Date', tickangle=0),
                  margin=dict(t=20, b=50, l=50, r=40),
                  height=350,
                 )


    fig = dict(data=data, layout=layout)
    line_graph = dcc.Graph(id='line-area-graph2', figure=fig, style={'display':'inline-block', 'width':'100%',
                                                                     'height':'100%;'})
    children = [line_graph]

    return children


@dash_example1.expanded_callback(
    dash.dependencies.Output('test-output-div2', 'children'),
    [dash.dependencies.Input('my-dropdown2', 'value')])
def callback_test2(*args, **kwargs):
    'Callback to exercise session functionality'

    print(args)
    print(kwargs)

    children = [html.Div(["You have selected %s." %(args[0])]),
                html.Div(["The session context message is '%s'" %(kwargs['session_state']['django_to_dash_context'])])]

    return children
