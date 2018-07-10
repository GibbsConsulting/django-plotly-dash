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
    'Check direct use of a stateless application'

    from django.urls import reverse
    url = reverse('the_django_plotly_dash:layout', kwargs={'ident':'SimpleExample'})

    response = client.get(url)

    assert response.content
    assert response.content == 'fghg'
    # TODO add more tests here
    assert False
