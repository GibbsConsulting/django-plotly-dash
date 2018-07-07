'Views for serving up dash applications and their constituents'

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
