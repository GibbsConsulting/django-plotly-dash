'''
Dash apps for the demonstration of functionality

Copyright (c) 2018 Gibbs Consulting and others - see CONTRIBUTIONS.md

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
'''

# pylint: disable=no-member

import uuid
import random

from datetime import datetime

import pandas as pd

from django.core.cache import cache

import dash
import dash_core_components as dcc
import dash_html_components as html

import plotly.graph_objs as go

import dpd_components as dpd

from dash.exceptions import PreventUpdate

from django_plotly_dash import DjangoDash
from django_plotly_dash.consumers import send_to_pipe_channel

#pylint: disable=too-many-arguments, unused-argument, unused-variable

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
        options=[{'label': i, 'value': j} for i, j in [('L', 'large'),
                                                       ('M', 'medium'),
                                                       ('S', 'small')]],
        value='medium'
    ),
    html.Div(id='output-size')

])

@app.callback(
    dash.dependencies.Output('output-color', 'children'),
    [dash.dependencies.Input('dropdown-color', 'value')])
def callback_color(dropdown_value):
    'Change output message'
    return "The selected color is %s." % dropdown_value

@app.callback(
    dash.dependencies.Output('output-size', 'children'),
    [dash.dependencies.Input('dropdown-color', 'value'),
     dash.dependencies.Input('dropdown-size', 'value')])
def callback_size(dropdown_color, dropdown_size):
    'Change output message'
    return "The chosen T-shirt is a %s %s one." %(dropdown_size,
                                                  dropdown_color)

a2 = DjangoDash("Ex2",
                serve_locally=True)

a2.layout = html.Div([
    dcc.RadioItems(id="dropdown-one",
                   options=[{'label':i, 'value':j} for i, j in [("O2", "Oxygen"),
                                                                ("N2", "Nitrogen"),
                                                                ("CO2", "Carbon Dioxide")]],
                   value="Oxygen"),
    html.Div(id="output-one")
    ])

@a2.expanded_callback(
    dash.dependencies.Output('output-one', 'children'),
    [dash.dependencies.Input('dropdown-one', 'value')]
    )
def callback_c(*args, **kwargs):
    'Update the output following a change of the input selection'
    #da = kwargs['dash_app']

    session_state = kwargs['session_state']

    calls_so_far = session_state.get('calls_so_far', 0)
    session_state['calls_so_far'] = calls_so_far + 1

    user_counts = session_state.get('user_counts', None)
    user_name = str(kwargs['user'])
    if user_counts is None:
        user_counts = {user_name:1}
        session_state['user_counts'] = user_counts
    else:
        user_counts[user_name] = user_counts.get(user_name, 0) + 1

    return "Args are [%s] and kwargs are %s" %(",".join(args), str(kwargs))

liveIn = DjangoDash("LiveInput",
                    serve_locally=True,
                    add_bootstrap_links=True)

liveIn.layout = html.Div([
    html.Div([html.Button('Choose red. Press me!',
                          id="red-button",
                          className="btn btn-danger"),
              html.Button('Blue is best. Pick me!',
                          id="blue-button",
                          className="btn btn-primary"),
              html.Button('Time to go green!',
                          id="green-button",
                          className="btn btn-success"),
             ], className="btn-group"),
    html.Div(id='button_local_counter', children="Press any button to start"),
    ], className="")

#pylint: disable=too-many-arguments
@liveIn.expanded_callback(
    dash.dependencies.Output('button_local_counter', 'children'),
    [dash.dependencies.Input('red-button', 'n_clicks'),
     dash.dependencies.Input('blue-button', 'n_clicks'),
     dash.dependencies.Input('green-button', 'n_clicks'),
     dash.dependencies.Input('red-button', 'n_clicks_timestamp'),
     dash.dependencies.Input('blue-button', 'n_clicks_timestamp'),
     dash.dependencies.Input('green-button', 'n_clicks_timestamp'),
    ],
    )
def callback_liveIn_button_press(red_clicks, blue_clicks, green_clicks,
                                 rc_timestamp, bc_timestamp, gc_timestamp, **kwargs): # pylint: disable=unused-argument
    'Input app button pressed, so do something interesting'

    if not rc_timestamp:
        rc_timestamp = 0
    if not bc_timestamp:
        bc_timestamp = 0
    if not gc_timestamp:
        gc_timestamp = 0

    if (rc_timestamp + bc_timestamp + gc_timestamp) < 1:
        change_col = None
        timestamp = 0
    else:
        if rc_timestamp > bc_timestamp:
            change_col = "red"
            timestamp = rc_timestamp
        else:
            change_col = "blue"
            timestamp = bc_timestamp

        if gc_timestamp > timestamp:
            timestamp = gc_timestamp
            change_col = "green"

        value = {'red_clicks':red_clicks,
                 'blue_clicks':blue_clicks,
                 'green_clicks':green_clicks,
                 'click_colour':change_col,
                 'click_timestamp':timestamp,
                 'user':str(kwargs.get('user', 'UNKNOWN'))}

        send_to_pipe_channel(channel_name="live_button_counter",
                             label="named_counts",
                             value=value)
    return "Number of local clicks so far is %s red and %s blue; last change is %s at %s" % (red_clicks,
                                                                                             blue_clicks,
                                                                                             change_col,
                                                                                             datetime.fromtimestamp(0.001*timestamp))

liveOut = DjangoDash("LiveOutput")

def _get_cache_key(state_uid):
    return "demo-liveout-s6-%s" % state_uid

def generate_liveOut_layout():
    'Generate the layout per-app, generating each tine a new uuid for the state_uid argument'
    return html.Div([
        dpd.Pipe(id="named_count_pipe",
                 value=None,
                 label="named_counts",
                 channel_name="live_button_counter"),
        html.Div(id="internal_state",
                 children="No state has been computed yet",
                 style={'display':'none'}),
        dcc.Graph(id="timeseries_plot"),
        dcc.Input(value=str(uuid.uuid4()),
                  id="state_uid",
                  style={'display':'none'},
                 )
        ])

liveOut.layout = generate_liveOut_layout

#pylint: disable=unused-argument
#@liveOut.expanded_callback(
@liveOut.callback(
    dash.dependencies.Output('internal_state', 'children'),
    [dash.dependencies.Input('named_count_pipe', 'value'),
     dash.dependencies.Input('state_uid', 'value'),],
    )
def callback_liveOut_pipe_in(named_count, state_uid, **kwargs):
    'Handle something changing the value of the input pipe or the associated state uid'

    cache_key = _get_cache_key(state_uid)
    state = cache.get(cache_key)

    # If nothing in cache, prepopulate
    if not state:
        state = {}

    # Guard against missing input on startup
    if not named_count:
        named_count = {}

    # extract incoming info from the message and update the internal state
    user = named_count.get('user', None)
    click_colour = named_count.get('click_colour', None)
    click_timestamp = named_count.get('click_timestamp', 0)

    if click_colour:
        colour_set = state.get(click_colour, None)

        if not colour_set:
            colour_set = [(None, 0, 100) for i in range(5)]

        _, last_ts, prev = colour_set[-1]

        # Loop over all existing timestamps and find the latest one
        if not click_timestamp or click_timestamp < 1:
            click_timestamp = 0

            for _, the_colour_set in state.items():
                _, lts, _ = the_colour_set[-1]
                if lts > click_timestamp:
                    click_timestamp = lts

            click_timestamp = click_timestamp + 1000

        if click_timestamp > last_ts:
            colour_set.append((user, click_timestamp, prev * random.lognormvariate(0.0, 0.1)),)
            colour_set = colour_set[-100:]

        state[click_colour] = colour_set
        cache.set(cache_key, state, 3600)

    return "(%s,%s)" % (cache_key, click_timestamp)

@liveOut.callback(
    dash.dependencies.Output('timeseries_plot', 'figure'),
    [dash.dependencies.Input('internal_state', 'children'),
     dash.dependencies.Input('state_uid', 'value'),],
    )
def callback_show_timeseries(internal_state_string, state_uid, **kwargs):
    'Build a timeseries from the internal state'

    cache_key = _get_cache_key(state_uid)
    state = cache.get(cache_key)

    # If nothing in cache, prepopulate
    if not state:
        state = {}

    colour_series = {}

    colors = {'red':'#FF0000',
              'blue':'#0000FF',
              'green':'#00FF00',
              'yellow': '#FFFF00',
              'cyan': '#00FFFF',
              'magenta': '#FF00FF',
              'black' : '#000000',
             }

    for colour, values in state.items():
        timestamps = [datetime.fromtimestamp(int(0.001*ts)) for _, ts, _ in values if ts > 0]
        #users = [user for user, ts, _ in values if ts > 0]
        levels = [level for _, ts, level in values if ts > 0]
        if colour in colors:
            colour_series[colour] = pd.Series(levels, index=timestamps).groupby(level=0).first()

    df = pd.DataFrame(colour_series).fillna(method="ffill").reset_index()[-25:]

    traces = [go.Scatter(y=df[colour],
                         x=df['index'],
                         name=colour,
                         line=dict(color=colors.get(colour, '#000000')),
                        ) for colour in colour_series]

    return {'data':traces,
            #'layout': go.Layout
           }

localState = DjangoDash("LocalState",
                        serve_locally=True)

localState.layout = html.Div([html.Img(src=localState.get_asset_url('image_one.png')),
                              html.Img(src='assets/image_two.png'),
                              ])

multiple_callbacks = DjangoDash("MultipleCallbackValues")

multiple_callbacks.layout = html.Div([
    html.Button("Press Me",
                id="button"),
    dcc.RadioItems(id='dropdown-color',
                   options=[{'label': c, 'value': c.lower()} for c in ['Red', 'Green', 'Blue']],
                   value='red'
                   ),
    html.Div(id="output-one"),
    html.Div(id="output-two"),
    html.Div(id="output-three")
    ])

@multiple_callbacks.callback(
    [dash.dependencies.Output('output-one', 'children'),
     dash.dependencies.Output('output-two', 'children'),
     dash.dependencies.Output('output-three', 'children')
     ],
    [dash.dependencies.Input('button', 'n_clicks'),
     dash.dependencies.Input('dropdown-color', 'value'),
     ])
def multiple_callbacks_one(button_clicks, color_choice):
    return ("Output 1: %s %s %s" % (button_clicks, color_choice, dash.callback_context.triggered),
            "Output 2: %s %s" % (color_choice, button_clicks),
            "Output 3: %s %s" % (button_clicks, color_choice),
            )


multiple_callbacks = DjangoDash("MultipleCallbackValuesExpanded")

multiple_callbacks.layout = html.Div([
    html.Button("Press Me",
                id="button"),
    dcc.RadioItems(id='dropdown-color',
                   options=[{'label': c, 'value': c.lower()} for c in ['Red', 'Green', 'Blue']],
                   value='red'
                   ),
    html.Div(id="output-one"),
    html.Div(id="output-two"),
    html.Div(id="output-three")
    ])

@multiple_callbacks.expanded_callback(
    [dash.dependencies.Output('output-one', 'children'),
     dash.dependencies.Output('output-two', 'children'),
     dash.dependencies.Output('output-three', 'children')
     ],
    [dash.dependencies.Input('button', 'n_clicks'),
     dash.dependencies.Input('dropdown-color', 'value'),
     ])
def multiple_callbacks_two(button_clicks, color_choice, **kwargs):
    if color_choice == 'green':
        raise PreventUpdate
    return ["Output 1: %s %s %s" % (button_clicks, color_choice, dash.callback_context.triggered),
            "Output 2: %s %s %s" % (button_clicks, color_choice, kwargs['callback_context'].triggered),
            "Output 3: %s %s [%s]" % (button_clicks, color_choice, kwargs)
            ]
