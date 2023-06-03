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
from json import JSONDecodeError

from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import redirect

from dash.exceptions import PreventUpdate

try:
    from dash.fingerprint import check_fingerprint
except:
    # check_fingerprint not available, fake it
    def check_fingerprint(resource):
        return resource, None


from .models import DashApp, check_stateless_loaded
from .util import get_initial_arguments, static_path

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

def layout(request, ident, stateless=False, cache_id=None, **kwargs):
    'Return the layout of the dash application'
    _, app = DashApp.locate_item(ident, stateless)

    view_func = app.locate_endpoint_function('dash-layout')
    resp = view_func()

    initial_arguments = get_initial_arguments(request, cache_id)

    response_data, mimetype = app.augment_initial_layout(resp, initial_arguments)
    return HttpResponse(response_data,
                        content_type=mimetype)

def update(request, ident, stateless=False, **kwargs):
    try:
        return _update(request, ident, stateless, **kwargs)
    except PreventUpdate:
        return HttpResponse(status=204)

def _update(request, ident, stateless=False, **kwargs):
    'Generate update json response'
    dash_app, app = DashApp.locate_item(ident, stateless)

    try:
        request_body = json.loads(request.body.decode('utf-8'))
    except (JSONDecodeError, UnicodeDecodeError):
        return HttpResponse(status=200)

    # Use direct dispatch with extra arguments in the argMap
    app_state = request.session.get("django_plotly_dash", dict())
    arg_map = {'dash_app_id': ident,
               'dash_app': dash_app,
               'user': request.user,
               'request':request,
               'session_state': app_state}
    resp = app.dispatch_with_args(request_body, arg_map)
    request.session['django_plotly_dash'] = app_state
    dash_app.handle_current_state()

    # Special for ws-driven edge case
    if str(resp) == 'EDGECASEEXIT':
        return HttpResponse("")

    # Change in returned value type
    try:
        rdata = resp.data
        rtype = resp.mimetype
    except:
        rdata = resp
        rtype = "application/json"

    return HttpResponse(rdata,
                        content_type=rtype)

def main_view(request, ident, stateless=False, cache_id=None, **kwargs):
    'Main view for a dash app'
    _, app = DashApp.locate_item(ident, stateless, cache_id=cache_id)

    view_func = app.locate_endpoint_function()
    resp = view_func()
    return HttpResponse(resp)

def component_component_suites(request, resource=None, component=None, **kwargs):
    'Return part of a client-side component, served locally for some reason'
    return component_suites(request,
                            resource=resource,
                            component=component,
                            extra_element="_components/",
                            **kwargs)


def component_suites_build(request, resource=None, component=None, extra_element="", cpe2=None, **kwargs):
    'Return part of a client-side component, served locally for some reason'
    return component_suites(request,
                            resource=resource,
                            component=component,
                            extra_element=extra_element,
                            cpe2=f"{cpe2}/build",
                            **kwargs)


def component_suites(request, resource=None, component=None, extra_element="", cpe2=None, **kwargs):
    'Return part of a client-side component, served locally for some reason'

    extra_path_part = f"{cpe2}/" if cpe2 else ""

    get_params = request.GET.urlencode()
    if get_params and False:
        redone_url = static_path("dash/component/%s/%s%s%s?%s" %(component, extra_path_part, extra_element, resource, get_params))
    else:
        resource, _fingerprint = check_fingerprint(resource)
        redone_url = static_path("dash/component/%s/%s%s%s" % (component, extra_path_part, extra_element, resource))

    return HttpResponseRedirect(redirect_to=redone_url)

def app_assets(request, **kwargs):
    'Return a local dash app asset, served up through the Django static framework'
    get_params = request.GET.urlencode()
    extra_part = ""
    if get_params:
        redone_url = static_path("dash/assets/%s?%s" %(extra_part, get_params))
    else:
        redone_url = static_path("dash/assets/%s" % extra_part)

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

def asset_redirection(request, path, ident=None, stateless=False, **kwargs):
    'Redirect static assets for a component'

    X, app = DashApp.locate_item(ident, stateless)

    # Redirect to a location based on the import path of the module containing the DjangoDash app
    static_path = X.get_asset_static_url(path)

    return redirect(static_path)

def add_stateless_apps(request, **kwargs):
    """Check all registered stateless apps and create ORM entries that are missing"""
    check_stateless_loaded()
    return redirect('admin:django_plotly_dash_statelessapp_changelist')

