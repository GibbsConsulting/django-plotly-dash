'''
Tests of django_plotly_dash.

These tests can be directly used or imported into eg the tests of the demo app.

The use of pytest is assumed.

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

import json
from unittest.mock import patch

import pytest
# pylint: disable=bare-except
from dash.dependencies import Input, State, Output
from django.urls import reverse

from django_plotly_dash import DjangoDash
from django_plotly_dash.dash_wrapper import get_local_stateless_list, get_local_stateless_by_name
from django_plotly_dash.models import DashApp, find_stateless_by_name
from django_plotly_dash.tests_dash_contract import fill_in_test_app, dash_contract_data


def test_dash_app():
    'Test the import and formation of the dash app orm wrappers'

    from django_plotly_dash.models import StatelessApp
    stateless_a = StatelessApp(app_name="Some name")

    assert stateless_a
    assert stateless_a.app_name
    assert str(stateless_a) == stateless_a.app_name


@pytest.mark.django_db
def test_dash_stateful_app_client_contract(client):
    'Test the state management of a DashApp as well as the contract between the client and the Dash app'

    from django_plotly_dash.models import StatelessApp

    # create a DjangoDash, StatelessApp and DashApp
    ddash = DjangoDash(name="DDash")
    fill_in_test_app(ddash, write=False)

    stateless_a = StatelessApp(app_name="DDash")
    stateless_a.save()
    stateful_a = DashApp(stateless_app=stateless_a,
                         instance_name="Some name",
                         slug="my-app", save_on_change=True)
    stateful_a.save()

    # check app can be found back
    assert "DDash" in get_local_stateless_list()
    assert get_local_stateless_by_name("DDash") == ddash
    assert find_stateless_by_name("DDash") == ddash

    # check the current_state is empty
    assert stateful_a.current_state() == {}

    # set the initial expected state
    expected_state = {'inp1': {'n_clicks': 0, 'n_clicks_timestamp': 1611733453854},
                      'inp1b': {'n_clicks': 5, 'n_clicks_timestamp': 1611733454354},
                      'inp2': {'n_clicks': 7, 'n_clicks_timestamp': 1611733454554},
                      'out1-0': {'n_clicks': 1, 'n_clicks_timestamp': 1611733453954},
                      'out1-1': {'n_clicks': 2, 'n_clicks_timestamp': 1611733454054},
                      'out1-2': {'n_clicks': 3, 'n_clicks_timestamp': 1611733454154},
                      'out1-3': {'n_clicks': 4, 'n_clicks_timestamp': 1611733454254},
                      'out1b': {'href': 'http://www.example.com/null',
                                'n_clicks': 6,
                                'n_clicks_timestamp': 1611733454454},
                      'out2-0': {'n_clicks': 8, 'n_clicks_timestamp': 1611733454654},
                      'out3': {'n_clicks': 12, 'n_clicks_timestamp': 1611733455054},
                      'out4': {'n_clicks': 16, 'n_clicks_timestamp': 1611733455454},
                      'out5': {'n_clicks': 20, 'n_clicks_timestamp': 1611733455854},
                      '{"_id":"inp-0","_type":"btn3"}': {'n_clicks': 9,
                                                         'n_clicks_timestamp': 1611733454754},
                      '{"_id":"inp-0","_type":"btn4"}': {'n_clicks': 13,
                                                         'n_clicks_timestamp': 1611733455154},
                      '{"_id":"inp-0","_type":"btn5"}': {'n_clicks': 17,
                                                         'n_clicks_timestamp': 1611733455554},
                      '{"_id":"inp-1","_type":"btn3"}': {'n_clicks': 10,
                                                         'n_clicks_timestamp': 1611733454854},
                      '{"_id":"inp-1","_type":"btn4"}': {'n_clicks': 14,
                                                         'n_clicks_timestamp': 1611733455254},
                      '{"_id":"inp-1","_type":"btn5"}': {'n_clicks': 18,
                                                         'n_clicks_timestamp': 1611733455654},
                      '{"_id":"inp-2","_type":"btn3"}': {'n_clicks': 11,
                                                         'n_clicks_timestamp': 1611733454954},
                      '{"_id":"inp-2","_type":"btn4"}': {'n_clicks': 15,
                                                         'n_clicks_timestamp': 1611733455354},
                      '{"_id":"inp-2","_type":"btn5"}': {'n_clicks': 19,
                                                         'n_clicks_timestamp': 1611733455754}}

    ########## test state management of the app and conversion of components ids
    # search for state values in dash layout
    stateful_a.populate_values()
    assert stateful_a.current_state() == expected_state
    assert stateful_a.have_current_state_entry("inp1", "n_clicks")
    assert stateful_a.have_current_state_entry({"_type": "btn3", "_id": "inp-0"}, "n_clicks_timestamp")
    assert stateful_a.have_current_state_entry('{"_id":"inp-0","_type":"btn3"}', "n_clicks_timestamp")
    assert not stateful_a.have_current_state_entry("checklist", "other-prop")

    # update a non existent state => no effect on current_state
    stateful_a.update_current_state("foo", "value", "random")
    assert stateful_a.current_state() == expected_state

    # update an existent state => update current_state
    stateful_a.update_current_state('{"_id":"inp-2","_type":"btn5"}', "n_clicks", 100)
    expected_state['{"_id":"inp-2","_type":"btn5"}'] = {'n_clicks': 100, 'n_clicks_timestamp': 1611733455754}
    assert stateful_a.current_state() == expected_state

    assert DashApp.objects.get(instance_name="Some name").current_state() == {}

    stateful_a.handle_current_state()

    assert DashApp.objects.get(instance_name="Some name").current_state() == expected_state

    # check initial layout serve has the correct values injected
    dash_instance = stateful_a.as_dash_instance()
    resp = dash_instance.serve_layout()

    # initialise layout with app state
    layout, mimetype = dash_instance.augment_initial_layout(resp, {})
    assert '"n_clicks": 100' in layout

    # initialise layout with initial arguments
    layout, mimetype = dash_instance.augment_initial_layout(resp, {
        '{"_id":"inp-2","_type":"btn5"}': {"n_clicks": 200}})
    assert '"n_clicks": 100' not in layout
    assert '"n_clicks": 200' in layout

    ########### test contract between client and app by replaying interactions recorded in tests_dash_contract.json
    # get update component route
    url = reverse('the_django_plotly_dash:update-component', kwargs={'ident': 'my-app'})

    # for all interactions in the tests_dash_contract.json
    for scenario in json.load(dash_contract_data.open("r")):
        body = scenario["body"]

        response = client.post(url, json.dumps(body), content_type="application/json")

        assert response.status_code == 200

        response = json.loads(response.content)

        # compare first item in response with first result
        result = scenario["result"]
        if isinstance(result, list):
            result = result[0]
        content = response["response"].popitem()[1].popitem()[1]
        assert content == result

        # handle state
        stateful_a.handle_current_state()

    # check final state has been changed accordingly
    final_state = {'inp1': {'n_clicks': 1, 'n_clicks_timestamp': 1615103027288},
                   'inp1b': {'n_clicks': 5, 'n_clicks_timestamp': 1615103033482},
                   'inp2': {'n_clicks': 8, 'n_clicks_timestamp': 1615103036591},
                   'out1-0': {'n_clicks': 1, 'n_clicks_timestamp': 1611733453954},
                   'out1-1': {'n_clicks': 2, 'n_clicks_timestamp': 1611733454054},
                   'out1-2': {'n_clicks': 3, 'n_clicks_timestamp': 1611733454154},
                   'out1-3': {'n_clicks': 4, 'n_clicks_timestamp': 1611733454254},
                   'out1b': {'href': 'http://www.example.com/1615103033482',
                             'n_clicks': 6,
                             'n_clicks_timestamp': 1611733454454},
                   'out2-0': {'n_clicks': 8, 'n_clicks_timestamp': 1611733454654},
                   'out3': {'n_clicks': 12, 'n_clicks_timestamp': 1611733455054},
                   'out4': {'n_clicks': 16, 'n_clicks_timestamp': 1611733455454},
                   'out5': {'n_clicks': 20, 'n_clicks_timestamp': 1611733455854},
                   '{"_id":"inp-0","_type":"btn3"}': {'n_clicks': 10,
                                                      'n_clicks_timestamp': 1615103039030},
                   '{"_id":"inp-0","_type":"btn4"}': {'n_clicks': 14,
                                                      'n_clicks_timestamp': 1611733455154},
                   '{"_id":"inp-0","_type":"btn5"}': {'n_clicks': 18,
                                                      'n_clicks_timestamp': 1611733455554},
                   '{"_id":"inp-1","_type":"btn3"}': {'n_clicks': 11,
                                                      'n_clicks_timestamp': 1615103039496},
                   '{"_id":"inp-1","_type":"btn4"}': {'n_clicks': 15,
                                                      'n_clicks_timestamp': 1611733455254},
                   '{"_id":"inp-1","_type":"btn5"}': {'n_clicks': 19,
                                                      'n_clicks_timestamp': 1611733455654},
                   '{"_id":"inp-2","_type":"btn3"}': {'n_clicks': 12,
                                                      'n_clicks_timestamp': 1615103040528},
                   '{"_id":"inp-2","_type":"btn4"}': {'n_clicks': 15,
                                                      'n_clicks_timestamp': 1611733455354},
                   '{"_id":"inp-2","_type":"btn5"}': {'n_clicks': 20,
                                                      'n_clicks_timestamp': 1611733455754}}

    assert DashApp.objects.get(instance_name="Some name").current_state() == final_state



def test_dash_callback_arguments():
    'Test the flexibility of the callback arguments order (handling of inputs/outputs/states)'

    # create a DjangoDash
    ddash = DjangoDash(name="DashCallbackArguments")

    # add a callback with the new flexible order of dependencies
    @ddash.callback(
        Output("one", "foo"),
        Output("two", "foo"),
        Input("one", "baz"),
        Input("two", "baz"),
        Input("three", "baz"),
        State("one", "bil"),
    )
    def new():
        pass

    # add a callback with the old/classical flexible order of dependencies
    @ddash.callback(
        [Output("one", "foo"),
         Output("two", "foo")],
        [Input("one", "baz"),
         Input("two", "baz"),
         Input("three", "baz")],
        [State("one", "bil")]
    )
    def old():
        pass

    assert ddash._callback_sets == [({'inputs': [Input("one", "baz"),
                                                 Input("two", "baz"),
                                                 Input("three", "baz"), ],
                                      'output': [Output("one", "foo"),
                                                 Output("two", "foo")],
                                      'prevent_initial_call': None,
                                      'state': [State("one", "bil"), ]},
                                     new),
                                    ({'inputs': [Input("one", "baz"),
                                                 Input("two", "baz"),
                                                 Input("three", "baz"), ],
                                      'output': [Output("one", "foo"),
                                                 Output("two", "foo")],
                                      'prevent_initial_call': None,
                                      'state': [State("one", "bil"), ]},
                                     old)
                                    ]


def test_util_error_cases(settings):
    'Test handling of missing settings'

    settings.PLOTLY_DASH = None

    from django_plotly_dash.util import pipe_ws_endpoint_name, dpd_http_endpoint_root, http_endpoint, insert_demo_migrations

    assert pipe_ws_endpoint_name() == 'dpd/ws/channel'
    assert dpd_http_endpoint_root() == "dpd/views"
    assert http_endpoint("fred") == '^dpd/views/fred/$'
    assert not insert_demo_migrations()

    del settings.PLOTLY_DASH

    assert pipe_ws_endpoint_name() == 'dpd/ws/channel'
    assert dpd_http_endpoint_root() == "dpd/views"
    assert http_endpoint("fred") == '^dpd/views/fred/$'
    assert not insert_demo_migrations()


def test_demo_routing():
    'Test configuration options for the demo'

    from django_plotly_dash.util import pipe_ws_endpoint_name, insert_demo_migrations
    assert pipe_ws_endpoint_name() == 'ws/channel'
    assert insert_demo_migrations()


def test_local_serving(settings):
    'Test local serve settings'

    from django_plotly_dash.util import serve_locally, static_asset_root, full_asset_path
    assert serve_locally() == settings.DEBUG
    assert static_asset_root() == 'dpd/assets'
    assert full_asset_path('fred.jim', 'harry') == 'dpd/assets/fred/jim/harry'


@pytest.mark.django_db
def test_direct_access(client):
    'Check direct use of a stateless application using demo test data'

    from django.urls import reverse
    from .app_name import main_view_label

    for route_name in ['layout', 'dependencies', main_view_label]:
        for prefix, arg_map in [('app-', {'ident':'SimpleExample'}),
                                ('', {'ident':'simpleexample-1'}),]:
            url = reverse('the_django_plotly_dash:%s%s' % (prefix, route_name), kwargs=arg_map)

            response = client.get(url)

            assert response.content
            assert response.status_code == 200

    for route_name in ['routes',]:
        for prefix, arg_map in [('app-', {'ident':'SimpleExample'}),
                                ('', {'ident':'simpleexample-1'}),]:
            url = reverse('the_django_plotly_dash:%s%s' % (prefix, route_name), kwargs=arg_map)

            did_fail = False
            try:
                response = client.get(url)
            except:
                did_fail = True

            assert did_fail


@pytest.mark.django_db
def test_updating(client):
    'Check updating of an app using demo test data'

    from django.urls import reverse

    route_name = 'update-component'

    for prefix, arg_map in [('app-', {'ident':'SimpleExample'}),
                            ('', {'ident':'simpleexample-1'}),]:
        url = reverse('the_django_plotly_dash:%s%s' % (prefix, route_name), kwargs=arg_map)

        response = client.post(url, json.dumps({'output': 'output-size.children',
                                                'inputs':[{'id':'dropdown-color',
                                                           'property':'value',
                                                           'value':'blue'},
                                                          {'id':'dropdown-size',
                                                           'property':'value',
                                                           'value':'medium'},
                                                         ]}), content_type="application/json")

        assert response.content == b'{"response":{"output-size":{"children":"The chosen T-shirt is a medium blue one."}},"multi":true}'
        assert response.status_code == 200


@pytest.mark.django_db
def test_injection_app_access(client):
    'Check direct use of a stateless application using demo test data'

    from django.urls import reverse
    from .app_name import main_view_label

    for route_name in ['layout', 'dependencies', main_view_label]:
        for prefix, arg_map in [('app-', {'ident':'dash_example_1'}),
                                #('', {'ident':'simpleexample-1'}),
                               ]:
            url = reverse('the_django_plotly_dash:%s%s' % (prefix, route_name), kwargs=arg_map)

            response = client.get(url)

            assert response.content
            assert response.status_code == 200

    for route_name in ['routes',]:
        for prefix, arg_map in [('app-', {'ident':'dash_example_1'}),]:
            url = reverse('the_django_plotly_dash:%s%s' % (prefix, route_name), kwargs=arg_map)

            did_fail = False
            try:
                response = client.get(url)
            except:
                did_fail = True

            assert did_fail



@pytest.mark.django_db
def test_injection_updating_multiple_callbacks(client):
    'Check updating of an app using demo test data for multiple callbacks'

    from django.urls import reverse

    route_name = 'update-component'

    for prefix, arg_map in [('app-', {'ident':'multiple_callbacks'}),]:
        url = reverse('the_django_plotly_dash:%s%s' % (prefix, route_name), kwargs=arg_map)

        # output is now a string of id and propery
        response = client.post(url, json.dumps({'output':'..output-one.children...output-two.children...output-three.children..',
                                                'inputs':[
            {'id':'button',
             'property':'n_clicks',
             'value':'10'},
            {'id':'dropdown-color',
             'property':'value',
             'value':'purple-ish yellow with a hint of greeny orange'},
                                                         ]}), content_type="application/json")

        assert response.status_code == 200

        resp = json.loads(response.content.decode('utf-8'))
        assert 'response' in resp

        resp_detail = resp['response']
        assert 'output-two' in resp_detail
        assert 'children' in resp_detail['output-two']
        assert resp_detail['output-two']['children'] == "Output 2: 10 purple-ish yellow with a hint of greeny orange []"


@pytest.mark.django_db
def test_flexible_expanded_callbacks(client):
    'Check updating of an app using demo test data for flexible expanded callbacks'

    from django.urls import reverse

    route_name = 'update-component'

    for prefix, arg_map in [('app-', {'ident':'flexible_expanded_callbacks'}),]:
        url = reverse('the_django_plotly_dash:%s%s' % (prefix, route_name), kwargs=arg_map)

        # output contains all arguments of the expanded_callback
        response = client.post(url, json.dumps({'output':'output-one.children',
                                                'inputs':[
            {'id':'button',
             'property':'n_clicks',
             'value':'10'},
                                                         ]}), content_type="application/json")

        assert response.status_code == 200

        resp = json.loads(response.content.decode('utf-8'))
        for key in ["dash_app_id", "dash_app", "callback_context"]:
            assert key in resp["response"]['output-one']['children']

        # output contains all arguments of the expanded_callback
        response = client.post(url, json.dumps({'output':'output-two.children',
                                                'inputs':[
            {'id':'button',
             'property':'n_clicks',
             'value':'10'},
                                                         ]}), content_type="application/json")

        assert response.status_code == 200

        resp = json.loads(response.content.decode('utf-8'))
        assert resp["response"]=={'output-two': {'children': 'ok'}}


        # output contains all arguments of the expanded_callback
        response = client.post(url, json.dumps({'output':'output-three.children',
                                                'inputs':[
            {'id':'button',
             'property':'n_clicks',
             'value':'10'},
                                                         ]}), content_type="application/json")

        assert response.status_code == 200

        resp = json.loads(response.content.decode('utf-8'))
        assert resp["response"]=={"output-three": {"children": "flexible_expanded_callbacks"}}


@pytest.mark.django_db
def test_injection_updating(client):
    'Check updating of an app using demo test data'

    from django.urls import reverse

    route_name = 'update-component'

    for prefix, arg_map in [('app-', {'ident':'dash_example_1'}),]:
        url = reverse('the_django_plotly_dash:%s%s' % (prefix, route_name), kwargs=arg_map)

        response = client.post(url, json.dumps({#'output':{'id':'test-output-div', 'property':'children'},
                                                'output': "test-output-div.children",
                                                'inputs':[{'id':'my-dropdown1',
                                                           'property':'value',
                                                           'value':'TestIt'},
                                                         ]}), content_type="application/json")

        rStart = b'{"response":{"test-output-div":{"children":[{"props":{"id":"line-area-graph2"'

        assert response.content.startswith(rStart)
        assert response.status_code == 200

        # Single output callback, output=="component_id.component_prop"
        response = client.post(url, json.dumps({'output':'test-output-div.children',
                                                'inputs':[{'id':'my-dropdown1',
                                                           'property':'value',
                                                           'value':'TestIt'},
                                                         ]}), content_type="application/json")

        rStart = b'{"response":{"test-output-div":{"children":[{"props":{"id":"line-area-graph2"'

        assert response.content.startswith(rStart)
        assert response.status_code == 200

        # Single output callback, fails if output=="..component_id.component_prop.."
        with pytest.raises(KeyError, match="..test-output-div.children.."):
            client.post(url, json.dumps({'output':'..test-output-div.children..',
                                                'inputs':[{'id':'my-dropdown1',
                                                           'property':'value',
                                                           'value':'TestIt'},
                                                         ]}), content_type="application/json")


        # Multiple output callback, fails if output=="component_id.component_prop"
        with pytest.raises(KeyError, match="test-output-div3.children"):
            client.post(url, json.dumps({'output':'test-output-div3.children',
                                                'inputs':[{'id':'my-dropdown1',
                                                           'property':'value',
                                                           'value':'TestIt'},
                                                         ]}), content_type="application/json")

        # Multiple output callback, output=="..component_id.component_prop.."
        response = client.post(url, json.dumps({'output':'..test-output-div3.children..',
                                                'inputs':[{'id':'my-dropdown1',
                                                           'property':'value',
                                                           'value':'TestIt'},
                                                         ]}), content_type="application/json")

        rStart = b'{"response":{"test-output-div3":{"children":[{"props":{"id":"line-area-graph2"'

        assert response.content.startswith(rStart)
        assert response.status_code == 200

        with pytest.raises(KeyError, match="django_to_dash_context"):
            client.post(url, json.dumps({'output': 'test-output-div2.children',
                                         'inputs':[{'id':'my-dropdown2',
                                                    'property':'value',
                                                    'value':'TestIt'},
                                                  ]}), content_type="application/json")

        session = client.session
        session['django_plotly_dash'] = {'django_to_dash_context': 'Test 789 content'}
        session.save()

        response = client.post(url, json.dumps({'output': 'test-output-div2.children',
                                                 'inputs':[{'id':'my-dropdown2',
                                                            'property':'value',
                                                            'value':'TestIt'},
                                                          ]}), content_type="application/json")
        rStart = b'{"response":{"test-output-div2":{"children":[{"props":{"children":["You have '

        assert response.content.startswith(rStart)
        assert response.status_code == 200

        assert response.content.find(b'Test 789 content') > 0


@pytest.mark.django_db
def test_argument_settings(settings, client):
    'Test the setting that controls how initial arguments are propagated through to the dash app'

    from django_plotly_dash.util import initial_argument_location, store_initial_arguments, get_initial_arguments

    assert initial_argument_location()

    settings.PLOTLY_DASH = {'cache_arguments': True}

    assert initial_argument_location()

    test_value = {"test":"first"}

    cache_id = store_initial_arguments(None, test_value)

    assert len(cache_id) > 10

    fetched = get_initial_arguments(None, cache_id)

    assert fetched == test_value

    settings.PLOTLY_DASH = {'cache_arguments': False}

    assert not initial_argument_location()

    cache_id2 = store_initial_arguments(client, test_value)

    assert len(cache_id2) > 10

    assert cache_id != cache_id2

    ## For some reason, sessions are continually replaced, so lookup here doesnt work
    #fetched2 = get_initial_arguments(client, cache_id2)
    #assert fetched2 == test_value

    assert store_initial_arguments(None, None) is None
    assert get_initial_arguments(None, None) is None
    assert store_initial_arguments(client, None) is None
    assert get_initial_arguments(client, None) is None


def test_stateless_lookup_noop():
    'Test no-op stateless lookup'

    from django_plotly_dash.util import stateless_app_lookup_hook
    lh_hook = stateless_app_lookup_hook()

    assert lh_hook is not None
    with pytest.raises(ImportError):
        lh_hook("not an app")


def test_middleware_artifacts():
    'Import and vaguely exercise middleware objects'

    from django_plotly_dash.middleware import EmbeddedHolder, ContentCollector

    eh = EmbeddedHolder()
    eh.add_css("some_css")
    eh.add_config("some_config")
    eh.add_scripts("some_scripts")

    assert eh.config == 'some_config'

    cc = ContentCollector()

    assert cc._encode("fred") == b'fred'


def test_finders():
    'Import and vaguely exercise staticfiles finders'

    from django_plotly_dash.finders import DashComponentFinder, DashAppDirectoryFinder, DashAssetFinder

    dcf = DashComponentFinder()
    dadf = DashAppDirectoryFinder()
    daf = DashAssetFinder()

    assert dcf is not None
    assert dadf is not None
    assert daf is not None


@pytest.mark.django_db
def test_app_loading(client):

    from django_plotly_dash.models import check_stateless_loaded
    from django.urls import reverse

    # Function should run wthout raising errors
    check_stateless_loaded()
    assert True

    url = reverse('the_django_plotly_dash:add_stateless_apps')

    response = client.post(url)

    # This view redirects to the main admin
    assert response.status_code == 302


@pytest.mark.django_db
def test_external_scripts_stylesheets(client):
    'Check external_stylesheets and external_scripts ends up in index'

    from demo.plotly_apps import external_scripts_stylesheets
    dash = external_scripts_stylesheets.as_dash_instance()

    with patch.object(dash, "interpolate_index") as mock:
        dash.index()

    _, kwargs = mock.call_args
    assert "https://codepen.io/chriddyp/pen/bWLwgP.css" in kwargs["css"]
    assert "https://stackpath.bootstrapcdn.com/bootstrap/4.1.3/css/bootstrap.min.css" in kwargs["css"]
    assert "https://www.google-analytics.com/analytics.js" in kwargs["scripts"]
    assert "https://cdn.polyfill.io/v2/polyfill.min.js" in kwargs["scripts"]
    assert "https://cdnjs.cloudflare.com/ajax/libs/lodash.js/4.17.10/lodash.core.js" in kwargs["scripts"]

def test_callback_decorator():
    inputs = [Input("one", "value"),
              Input("two", "value"),
              ]
    states = [Input("three", "value"),
              Input("four", "value"),
              ]

    def callback_standard(one, two, three, four):
        return

    assert DjangoDash.get_expanded_arguments(callback_standard, inputs, states) == []

    def callback_standard(one, two, three, four, extra_1):
        return

    assert DjangoDash.get_expanded_arguments(callback_standard, inputs, states) == ['extra_1']

    def callback_args(one, *args):
        return

    assert DjangoDash.get_expanded_arguments(callback_args, inputs, states) == []

    def callback_args_extra(one, *args, extra_1):
        return

    assert DjangoDash.get_expanded_arguments(callback_args_extra, inputs, states) == ['extra_1' ]

    def callback_args_extra_star(one, *, extra_1):
        return

    assert DjangoDash.get_expanded_arguments(callback_args_extra_star, inputs, states) == ['extra_1' ]


    def callback_kwargs(one, two, three, four, extra_1, **kwargs):
        return

    assert DjangoDash.get_expanded_arguments(callback_kwargs, inputs, states) == None

    def callback_kwargs(one, two, three, four, *, extra_1, **kwargs, ):
        return

    assert DjangoDash.get_expanded_arguments(callback_kwargs, inputs, states) == None
