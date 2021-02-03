"""Test helpers to configure an app that tests many cases (single/multiple outputs, patterns, multi triggers, ...).


"""

import json
from functools import wraps
from pathlib import Path
from typing import Union

import dash
import dash_html_components as html
import flask
from dash import Dash, no_update
from dash.dependencies import MATCH, ALL, ALLSMALLER, Input, Output, State
from dash.development.base_component import Component
from flask import request

from django_plotly_dash import DjangoDash

dash_contract_data = Path(__file__).with_suffix(".json")


def fill_in_test_app(app: Union[DjangoDash, Dash], write=False):
    """Takes an unitialized Dash (or DjangoDash) app and add dash components and callbacks to test
    - single/multiple outputs
    - patterns (ALL,ALLSMALLER,MATCH)
    - multi triggers

    :param app: the Dash/DjangoDash app to initialize with components and callbacks
    :param write: if True, it will record/log in the tests_dash_contract.json all client callbacks to the app
    :return: None
    """

    # define decorator that logs the body/response if write==True
    if not write:
        log_body_response = lambda f: f
    else:
        record_session = dash_contract_data.open("w")
        record_session.write("[")

        def log_body_response(f):
            @wraps(f)
            def wrapper(*args, **kwargs):
                result = f(*args, **kwargs)
                record_session.write(
                    json.dumps(
                        {
                            "body": flask.request.get_json(),
                            "args": args,
                            "kwargs": kwargs,
                            "result": result,
                        }
                    )
                )
                record_session.write(",")
                return result

            return wrapper

    def add_outputs_multi():
        """Test output format (in list or not)"""
        inp1 = html.Button("Multi-single-output", id="inp1")
        outs = [html.Div(id=f"out1-{i}") for i in range(4)]

        app.layout.children.append(html.Div([inp1] + outs))

        @app.callback(
            Output(outs[0].id, "children"),
            [Input(inp1.id, "n_clicks_timestamp")],
            [State(inp1.id, "n_clicks")],
        )
        @log_body_response
        def test_single_output(*args):
            return f"single - {args}"

        @app.callback(
            [Output(outs[1].id, "children")],
            [Input(inp1.id, "n_clicks_timestamp")],
            [State(inp1.id, "n_clicks")],
        )
        @log_body_response
        def test_single_output_list(*args):
            return [f"single in list - {args}"]

        @app.callback(
            [Output(outs[2].id, "children"), Output(outs[3].id, "children")],
            [Input(inp1.id, "n_clicks_timestamp")],
            [State(inp1.id, "n_clicks")],
        )
        @log_body_response
        def test_multi_output(*args):
            return [f"multi in list - {args}"] * 2

    def add_multi_triggered():
        """Test a callback getting more than one element in the triggered context"""
        inp1 = html.Button("Multiple triggered", id="inp2")
        outs = [html.Div(id=f"out2-{i}") for i in range(1)]

        app.layout.children.append(html.Div([inp1] + outs))

        @app.callback(
            Output(outs[0].id, "children"),
            [Input(inp1.id, "n_clicks_timestamp"), Input(inp1.id, "n_clicks")],
        )
        @log_body_response
        def test_single_output(*args, **kwargs):
            print(kwargs)
            return f"multi triggered - {args} - {dash.callback_context.triggered or []}"

    def add_pattern_all():
        inps = [
            html.Button(f"Pattern ALL {i}", id={"_id": f"inp-{i}", "_type": "btn3"})
            for i in range(3)
        ]
        out = html.Div(id=f"out3")

        app.layout.children.append(html.Div(inps + [out]))

        @app.callback(
            Output(out.id, "children"),
            [Input({"_id": ALL, "_type": "btn3"}, "n_clicks_timestamp")],
            [State({"_id": ALL, "_type": "btn3"}, "n_clicks")],
        )
        @log_body_response
        def test_single_output(*args):
            return f"pattern ALL - {args}"

    def add_pattern_allsmaller():
        inps = [
            html.Button(f"Pattern ALLSMALLER {i}", id={"_id": f"inp-{i}", "_type": "btn4"})
            for i in range(3)
        ]
        out = html.Div(id=f"out4")

        app.layout.children.append(html.Div(inps + [out]))

        @app.callback(
            Output({"_id": MATCH, "_type": "btn4"}, "children"),
            [Input({"_id": ALLSMALLER, "_type": "btn4"}, "n_clicks")],
            [State({"_id": ALLSMALLER, "_type": "btn4"}, "id")],
        )
        @log_body_response
        def test_single_output(*args):
            return f"pattern ALLSMALLER - {args}"

    def add_pattern_match():
        inps = [
            html.Button(f"Pattern MATCH {i}", id={"_id": f"inp-{i}", "_type": "btn5"})
            for i in range(3)
        ]
        out = html.Div(id=f"out5")

        app.layout.children.append(html.Div(inps + [out]))

        @app.callback(
            Output({"_id": MATCH, "_type": "btn5"}, "children"),
            [Input({"_id": MATCH, "_type": "btn5"}, "n_clicks")],
            [State({"_id": MATCH, "_type": "btn5"}, "id")],
        )
        @log_body_response
        def test_single_output(*args):
            return f"pattern MATCH - {args}"

    def add_stop():
        app.layout.children.append(html.Button("stop", id="stop"))

        @app.callback(Output("stop", "children"), [Input("stop", "n_clicks")])
        def stop_server(nclicks):
            if nclicks:
                if write:
                    # close the file recording the session
                    record_session.write("]")
                    record_session.close()
                func = request.environ.get("werkzeug.server.shutdown")
                func()
            return no_update

    app.layout = html.Div([])
    add_outputs_multi()
    add_multi_triggered()
    add_pattern_all()
    add_pattern_allsmaller()
    add_pattern_match()
    add_stop()

    # add to all elements a n_clicks/n_clicks_timestamp values to have populate_values detect properties
    i = 0
    ts = 1611733453854
    for comp in app.layout.children:
        for elem in comp.children:
            if isinstance(elem, Component):
                elem.n_clicks = i
                elem.n_clicks_timestamp = ts
                i += 1
                ts += 100


if __name__ == "__main__":
    # to generate the test_dash_contract.json, run the pure Dash app and click on each button once successively
    # if you regenerate the test_dash_contract.json, the final assert of the test test_dash_stateful_app will fail
    # as the timestamp will be different => the test will have to be updated accordingly
    test_app = Dash("DashContractApp")

    fill_in_test_app(test_app, write=True)

    test_app.run_server(debug=True)
