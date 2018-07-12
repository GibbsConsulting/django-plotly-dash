'Dash apps for the demonstration of functionality'

# pylint: disable=no-member

import uuid

from django.core.cache import cache

import dash
import dash_core_components as dcc
import dash_html_components as html

import dpd_components as dpd

from django_plotly_dash import DjangoDash
from django_plotly_dash.consumers import send_to_pipe_channel

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
    dpd.Pipe(id="button_count",
             value=0,
             label="button count",
             channel_name="live_button_counter"),
    html.Div([html.Button('Choose red. Press me!',
                          id="red-button",
                          className="btn btn-danger"),
              html.Button('Blue is best. Pick me!',
                          id="blue-button",
                          className="btn btn-primary"),
              ], className="btn-group"),
    html.Div(id='button_local_counter', children="Press any button to start"),
    ], className="")

@liveIn.expanded_callback(
    dash.dependencies.Output('button_local_counter', 'children'),
    [dash.dependencies.Input('red-button', 'n_clicks'),
     dash.dependencies.Input('blue-button', 'n_clicks'),
     dash.dependencies.Input('red-button', 'n_clicks_timestamp'),
     dash.dependencies.Input('blue-button', 'n_clicks_timestamp'),
    ],
    )
def callback_liveIn_button_press(red_clicks, blue_clicks, *args, **kwargs): # pylint: disable=unused-argument
    'Input app button pressed, so do something interesting'
    send_to_pipe_channel(channel_name="live_button_counter",
                         label="named_counts",
                         value={'red_clicks':red_clicks,
                                'blue_clicks':blue_clicks,
                                'user':str(kwargs.get('user', 'UNKNOWN'))})
    return "Number of local clicks so far is %s red and %s blue at %s" % (red_clicks, blue_clicks, str(args))

liveOut = DjangoDash("LiveOutput",
                     serve_locally=True)

def generate_liveOut_layout():
    'Generate the layout per-app, generating each tine a new uuid for the state_uid argument'
    return html.Div([
        dpd.Pipe(id="named_count_pipe",
                 value=None,
                 label="named_counts",
                 channel_name="live_button_counter"),
        html.Div(id="local_output",
                 children="Output goes here"),
        dcc.Input(value=str(uuid.uuid4()),
                  id="state_uid",
                  style={'display':'none'},
                 )
        ])

liveOut.layout = generate_liveOut_layout

#@liveOut.expanded_callback(
@liveOut.callback(
    dash.dependencies.Output('local_output', 'children'),
    [dash.dependencies.Input('named_count_pipe', 'value'),
     dash.dependencies.Input('state_uid', 'value'),],
    )
def callback_liveOut_pipe_in(named_count, state_uid, **kwargs):
    'Handle something changing the value of the input pipe or the associated state uid'

    cache_key = "liveout-state-%s" % state_uid
    state = cache.get(cache_key)

    # If nothing in cache, prepopulate
    if not state:
        state = {}

    # First call for this widget has no named_count value
    if named_count is None:
        named_count = {}

    user = named_count.get('user', None)
    if user is not None:
        ucr = named_count.get('red_clicks', 0)
        ucb = named_count.get('blue_clicks', 0)

        try:
            cr, cb = state.get(user)
        except:
            cr = 0
            cb = 0

        if ucr is not None:
            cr += ucr
        if ucb is not None:
            cb += ucb

        state[user] = (cr, cb)

    cache.set(cache_key, state, 60)

    return "Liveout got %s and state is %s for instance %s" %(str(kwargs), str(state), state_uid)
