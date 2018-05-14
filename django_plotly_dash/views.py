from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse

import json

from .models import DashApp
from .dash_wrapper import get_stateless_by_name

def routes(*args,**kwargs):
    raise NotImplementedError

def dependencies(request, id, stateless=False, **kwargs):
    if stateless:
        da = get_stateless_by_name(id)
    else:
        da = get_object_or_404(DashApp,slug=id)

    app = da.as_dash_instance()

    with app.app_context():
        mFunc = app.locate_endpoint_function('dash-dependencies')
        resp = mFunc()
        return HttpResponse(resp.data,
                            content_type=resp.mimetype)

def layout(request, id, stateless=False, **kwargs):
    if stateless:
        da = get_stateless_by_name(id)
    else:
        da = get_object_or_404(DashApp,slug=id)
    app = da.as_dash_instance()

    mFunc = app.locate_endpoint_function('dash-layout')
    resp = mFunc()
    return app.augment_initial_layout(resp)

def update(request, id, stateless=False, **kwargs):
    if stateless:
        da = get_stateless_by_name(id)
    else:
        da = get_object_or_404(DashApp,slug=id)
    app = da.as_dash_instance()

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
        argMap = {'id':id,
                  'session':request.session}
        resp = app.dispatch_with_args(rb, argMap)

    return HttpResponse(resp.data,
                        content_type=resp.mimetype)

def main_view(request, id, stateless=False, **kwargs):
    if stateless:
        da = get_stateless_by_name(id)
    else:
        da = get_object_or_404(DashApp,slug=id)
    app = da.as_dash_instance()

    mFunc = app.locate_endpoint_function()
    resp = mFunc()
    return HttpResponse(resp)

