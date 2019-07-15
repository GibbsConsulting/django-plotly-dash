'''
Test demo appliction

Most of these tests are simply the loading of the individual files that
constitute the demo. A configuration failure would
cause one or more of these to fail.

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

def test_stateless_lookup():
    'Test side loading of stateless apps'

    from django_plotly_dash.util import stateless_app_lookup_hook
    lh_hook = stateless_app_lookup_hook()

    with pytest.raises(ImportError):
        lh_hook("not a real app name")

    demo_app = lh_hook('demo_app')

    assert demo_app is not None
    assert demo_app._uid == 'name_of_demo_app'

