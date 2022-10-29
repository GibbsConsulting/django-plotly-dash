'''
Dash bootstrap component demo app

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

import dash
import dash_bootstrap_components as dbc
from dash import html

from django_plotly_dash import DjangoDash

dd = DjangoDash("BootstrapApplication",
                serve_locally=True,
                add_bootstrap_links=True)

dd.layout = html.Div(
    [
        dbc.Alert("This is an alert", color="primary"),
        dbc.Alert("Danger", color="danger"),
        dbc.Checklist(id='check_switch', switch=True, options=[{"label": "An example switch", "value": 1}], value=[0]),
        dbc.Checklist(id='check_check', switch=False, options=[{"label": "An example checkbox", "value": 1}], value=[0]),
        ]
    )

dis = DjangoDash("DjangoSessionState",
                 add_bootstrap_links=True)

dis.layout = html.Div(
    [
        dbc.Alert("This is an alert", id="base-alert", color="primary"),
        dbc.Alert(children="Danger", id="danger-alert", color="danger"),
        dbc.Button("Update session state", id="update-button", color="warning"),
        ]
    )

#pylint: ignore=unused-argument
@dis.expanded_callback(
    dash.dependencies.Output("base-alert", 'children'),
    [dash.dependencies.Input('danger-alert', 'children'),]
    )
def session_demo_danger_callback(da_children, session_state=None, **kwargs):
    'Update output based just on state'
    if not session_state:
        return "Session state not yet available"

    return "Session state contains: " + str(session_state.get('bootstrap_demo_state', "NOTHING")) + " and the page render count is " + str(session_state.get("ind_use", "NOT SET"))

#pylint: ignore=unused-argument
@dis.expanded_callback(
    dash.dependencies.Output("danger-alert", 'children'),
    [dash.dependencies.Input('update-button', 'n_clicks'),]
    )
def session_demo_alert_callback(n_clicks, session_state=None, **kwargs):
    'Output text based on both app state and session state'
    if session_state is None:
        raise NotImplementedError("Cannot handle a missing session state")
    csf = session_state.get('bootstrap_demo_state', None)
    if not csf:
        csf = dict(clicks=0, overall=0)
    else:
        csf['clicks'] = n_clicks
        if n_clicks is not None and n_clicks > csf.get('overall_max',0):
            csf['overall_max'] = n_clicks
    session_state['bootstrap_demo_state'] = csf
    return "Button has been clicked %s times since the page was rendered" %n_clicks

