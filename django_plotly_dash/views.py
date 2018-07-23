'''
Views for serving up dash applications and their constituents

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

 # pylint: disable=unused-argument

import json

from django.http import HttpResponse, HttpResponseRedirect

from .models import DashApp

def routes(*args, **kwargs):
    'Return routes'
    raise NotImplementedError

def dependencies(request, ident, stateless=False, **kwargs):
    'Return the dependencies'
    _, app = DashApp.locate_item(ident, stateless)

    with app.app_context():
        view_func = app.locate_endpoint_function('dash-dependencies')
        resp = view_func()
        return HttpResponse(resp.data,
                            content_type=resp.mimetype)

def layout(request, ident, stateless=False, **kwargs):
    'Return the layout of the dash application'
    _, app = DashApp.locate_item(ident, stateless)

    view_func = app.locate_endpoint_function('dash-layout')
    resp = view_func()
    response_data, mimetype = app.augment_initial_layout(resp)
    return HttpResponse(response_data,
                        content_type=mimetype)

def update(request, ident, stateless=False, **kwargs):
    'Generate update json response'
    dash_app, app = DashApp.locate_item(ident, stateless)

    request_body = json.loads(request.body.decode('utf-8'))

    if app.use_dash_dispatch():
        # Force call through dash
        view_func = app.locate_endpoint_function('dash-update-component')

        import flask
        with app.test_request_context():
            # Fudge request object
            # pylint: disable=protected-access
            flask.request._cached_json = (request_body, flask.request._cached_json[True])
            resp = view_func()
    else:
        # Use direct dispatch with extra arguments in the argMap
        app_state = request.session.get("django_plotly_dash", dict())
        arg_map = {'dash_app_id': ident,
                   'dash_app': dash_app,
                   'user': request.user,
                   'session_state': app_state}
        resp = app.dispatch_with_args(request_body, arg_map)
        request.session['django_plotly_dash'] = app_state
        dash_app.handle_current_state()

    # Special for ws-driven edge case
    if str(resp) == 'EDGECASEEXIT':
        return HttpResponse("")

    return HttpResponse(resp.data,
                        content_type=resp.mimetype)

def main_view(request, ident, stateless=False, **kwargs):
    'Main view for a dash app'
    _, app = DashApp.locate_item(ident, stateless)

    view_func = app.locate_endpoint_function()
    resp = view_func()
    return HttpResponse(resp)

def component_suites(request, resource=None, component=None, **kwargs):
    'Return part of a client-side component, served locally for some reason'

    get_params = request.GET.urlencode()
    if get_params:
        redone_url = "/static/dash/%s/%s?%s" %(component, resource, get_params)
    else:
        redone_url = "/static/dash/%s/%s" %(component, resource)

    return HttpResponseRedirect(redirect_to=redone_url)


# pylint: disable=wrong-import-position, wrong-import-order
from django.template.response import TemplateResponse

def add_to_session(request, template_name="index.html", **kwargs):
    'Add some info to a session in a place that django-plotly-dash can pass to a callback'

    django_plotly_dash = request.session.get("django_plotly_dash", dict())

    session_add_count = django_plotly_dash.get('add_counter', 0)
    django_plotly_dash['add_counter'] = session_add_count + 1
    request.session['django_plotly_dash'] = django_plotly_dash

    return TemplateResponse(request, template_name, {})
