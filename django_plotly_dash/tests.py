'''
Tests of django_plotly_dash.

These tests can be directly used or imported into eg the tests of the demo app
'''

import pytest

def test_dash_app():
    'Test the import and formation of the dash app orm wrappers'

    from django_plotly_dash.models import StatelessApp
    stateless_a = StatelessApp(app_name="Some name")

    assert stateless_a
    assert stateless_a.app_name

def test_util_error_cases(settings):

    settings.PLOTLY_DASH = None

    from django_plotly_dash.util import pipe_ws_endpoint_name

    # TODO provide a separate function that has settings as an argument
    assert pipe_ws_endpoint_name() == 'ws/channel'

@pytest.mark.django_db
def test_direct_access(client):

    from django.urls import reverse
    url = reverse('the_django_plotly_dash:layout',kwargs={'ident':'SimpleExample'})

    response = client.get(url)

    assert response.content
    # TODO add more tests here
    assert False
