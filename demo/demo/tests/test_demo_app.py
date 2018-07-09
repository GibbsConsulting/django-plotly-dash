'''
Test demo appliction

Most of these tests are simply the loading of the individual files that
constitute the demo. A configuration failure would
cause one or more of these to fail.
'''

# pylint: disable=protected-access, no-member
import pytest

def test_asgi_loading():
    'Test loading of a module'
    from ..asgi import application
    assert application

def test_wsgi_loading():
    'Test loading of a module'
    from ..wsgi import application
    assert application

def test_routing_loading():
    'Test loading of a module'
    from ..routing import application
    assert application

def test_url_loading():
    'Test loading of a module'
    from ..urls import urlpatterns
    assert urlpatterns

def test_demo_loading():
    'Test the import and formation of a dash example app'

    from ..plotly_apps import app

    assert app._uid == 'SimpleExample' # pylint: disable=protected-access

    assert app.layout

@pytest.mark.django_db
def test_app_lookup():
    'Test looking up an existing application'
    from ..plotly_apps import app

    from django_plotly_dash.models import get_stateless_by_name, StatelessApp

    app2 = get_stateless_by_name(app._uid)

    assert app2
    assert app._uid == app2._uid

    app3 = StatelessApp.objects.get(app_name=app._uid)

    assert app3
    assert app3.app_name == app2._uid

def test_app_callbacks():
    'Test the callbacks of the demo applications'

    from ..plotly_apps import app, a2, liveIn, liveOut

    assert app
    assert a2
    assert liveIn
    assert liveOut

    # TODO need something to trigger callbacks
