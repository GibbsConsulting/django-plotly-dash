from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse, HttpResponseRedirect

import json

from .models import DashApp

def routes(*args,**kwargs):
    raise NotImplementedError

def dependencies(request, id, stateless=False, **kwargs):
    da, app = DashApp.locate_item(id, stateless)

    with app.app_context():
        mFunc = app.locate_endpoint_function('dash-dependencies')
        resp = mFunc()
        return HttpResponse(resp.data,
                            content_type=resp.mimetype)

def layout(request, id, stateless=False, **kwargs):
    da, app = DashApp.locate_item(id, stateless)

    mFunc = app.locate_endpoint_function('dash-layout')
    resp = mFunc()
    response_data, mimetype = app.augment_initial_layout(resp)
    return HttpResponse(response_data,
                        content_type=mimetype)

def update(request, id, stateless=False, **kwargs):
    da, app = DashApp.locate_item(id, stateless)

    rb = json.loads(request.body.decode('utf-8'))

    if app.use_dash_dispatch():
        # Force call through dash
        mFunc = app.locate_endpoint_function('dash-update-component')

        import flask
        with app.test_request_context():
            # Fudge request object
            flask.request._cached_json = (rb, flask.request._cached_json[True])
            resp = mFunc()
    else:
        # Use direct dispatch with extra arguments in the argMap
        app_state = request.session.get("django_plotly_dash",dict())
        argMap = {'dash_app_id': id,
                  'dash_app': da,
                  'user': request.user,
                  'session_state': app_state}
        resp = app.dispatch_with_args(rb, argMap)
        request.session['django_plotly_dash'] = app_state
        da.handle_current_state()

    return HttpResponse(resp.data,
                        content_type=resp.mimetype)

def main_view(request, id, stateless=False, **kwargs):
    da, app = DashApp.locate_item(id, stateless)

    mFunc = app.locate_endpoint_function()
    resp = mFunc()
    return HttpResponse(resp)

def component_suites(request, resource=None, component=None, **kwargs):

    eBig = request.GET.urlencode()
    if len(eBig) > 0:
        redone_url = "/static/dash/%s/%s?%s" %(component, resource, eBig)
    else:
        redone_url = "/static/dash/%s/%s" %(component, resource)

    return HttpResponseRedirect(redirect_to=redone_url)
