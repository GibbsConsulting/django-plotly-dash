import dash
import dash_core_components as dcc
import dash_html_components as html

import dpd_components as dpd

from django_plotly_dash import DjangoDash, send_to_pipe_channel

import uuid

from django.core.cache import cache

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

a2 = DjangoDash("Ex2",
                serve_locally=True)
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

    session_state = kwargs['session_state']

    calls_so_far = session_state.get('calls_so_far',0)
    session_state['calls_so_far'] = calls_so_far + 1

    user_counts = session_state.get('user_counts',None)
    user_name = str(kwargs['user'])
    if user_counts is None:
        user_counts = {user_name:1}
        session_state['user_counts'] = user_counts
    else:
        user_counts[user_name] = user_counts.get(user_name,0) + 1

    return "Args are [%s] and kwargs are %s" %(",".join(args),str(kwargs))

liveIn = DjangoDash("LiveInput",
                    serve_locally=True)
liveIn.layout = html.Div([
    dpd.Pipe(id="button_count",
             value=0,
             label="button count",
             channel_name="live_button_counter"),
    html.Button('Press me!', id="button"),
    html.Div(id='button_local_counter',children="Press the button to get going"),
    ])

@liveIn.expanded_callback(
    dash.dependencies.Output('button_local_counter','children'),
    [dash.dependencies.Input('button','n_clicks'),],
    )
def callback_liveIn_button_press(n_clicks, *args, **kwargs):
    send_to_pipe_channel(channel_name="live_button_counter",
                         label="named_counts",
                         value={'n_clicks':n_clicks,
                                'user':str(kwargs.get('user','UNKNOWN'))})
    return "Numnber of local clicks so far is %s" % n_clicks

liveOut = DjangoDash("LiveOutput",
                     serve_locally=True)

def generate_liveOut_layout():
    return html.Div([
        dpd.Pipe(id="named_count_pipe",
                 value=None,
                 label="named_counts",
                 channel_name="live_button_counter"),
        html.Div(id="local_output",
                 children="Output goes here"),
        dcc.Input(value=str(uuid.uuid4()),
                 id="state_uid",
                 #style={'display':'none'})
                  )
        ])

liveOut.layout = generate_liveOut_layout

#@liveOut.expanded_callback(
@liveOut.callback(
    dash.dependencies.Output('local_output','children'),
    [dash.dependencies.Input('named_count_pipe','value'),
     dash.dependencies.Input('state_uid','value'),],
    )
def callback_liveOut_pipe_in(named_count, state_uid, **kwargs):

    cache_key = "liveout-state-%s" % state_uid
    state = cache.get(cache_key)

    # If nothing in cache, prepopulate
    if not state:
        state = {}

    # First call for this widget has no named_count value
    if named_count is None:
        named_count = {}

    user = named_count.get('user',"NONE")
    uc = named_count.get('n_clicks',0)

    if uc is None:
        uc = 0

    state[user] = uc + state.get(user,0)

    cache.set(cache_key, state, 60)

    return "Liveout got %s and state is %s for instance %s" %(str(kwargs),str(state),state_uid)

