'''
Tests of django_plotly_dash.

These tests can be directly used or imported into eg the tests of the demo app.

The use of pytest is assumed.
'''

import pytest

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

def test_demo_routing():
    'Test configuration options for the demo'

    from django_plotly_dash.util import pipe_ws_endpoint_name, insert_demo_migrations
    assert pipe_ws_endpoint_name() == 'ws/channel'
    assert insert_demo_migrations()

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

@pytest.mark.django_db
def test_updating(client):
    'Check updating of an app using demo test data'

    import json
    from django.urls import reverse

    route_name = 'update-component'

    for prefix, arg_map in [('app-', {'ident':'SimpleExample'}),
                            ('', {'ident':'simpleexample-1'}),]:
        url = reverse('the_django_plotly_dash:%s%s' % (prefix, route_name), kwargs=arg_map)

        response = client.post(url, json.dumps({'output':{'id':'output-size', 'property':'children'},
                                                'inputs':[{'id':'dropdown-color',
                                                           'property':'value',
                                                           'value':'blue'},
                                                          {'id':'dropdown-size',
                                                           'property':'value',
                                                           'value':'medium'},
                                                         ]}), content_type="application/json")

        assert response.content == b'{"response": {"props": {"children": "The chosen T-shirt is a medium blue one."}}}'
        assert response.status_code == 200
