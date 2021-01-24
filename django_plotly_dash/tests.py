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

import pytest
import json

#pylint: disable=bare-except
from dash.dependencies import Input

from django_plotly_dash import DjangoDash


def test_dash_app():
    'Test the import and formation of the dash app orm wrappers'

    from django_plotly_dash.models import StatelessApp
    stateless_a = StatelessApp(app_name="Some name")

    assert stateless_a
    assert stateless_a.app_name
    assert str(stateless_a) == stateless_a.app_name


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

        assert response.content == b'{"response": {"output-size": {"children": "The chosen T-shirt is a medium blue one."}}, "multi": true}'
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

        rStart = b'{"response": {"test-output-div": {"children": [{"props": {"id": "line-area-graph2"'

        assert response.content.startswith(rStart)
        assert response.status_code == 200

        # Single output callback, output=="component_id.component_prop"
        response = client.post(url, json.dumps({'output':'test-output-div.children',
                                                'inputs':[{'id':'my-dropdown1',
                                                           'property':'value',
                                                           'value':'TestIt'},
                                                         ]}), content_type="application/json")

        rStart = b'{"response": {"test-output-div": {"children": [{"props": {"id": "line-area-graph2"'

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

        rStart = b'{"response": {"test-output-div3": {"children": [{"props": {"id": "line-area-graph2"'

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
        rStart = b'{"response": {"test-output-div2": {"children": [{"props": {"children": ["You have '

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
