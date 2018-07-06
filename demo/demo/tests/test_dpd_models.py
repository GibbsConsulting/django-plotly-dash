'''
Test dpd demo

Most of these tests are simply the loading of the individual files that
constitute the demo. A configuration failure would
cause one or more of these to fail.
'''

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
