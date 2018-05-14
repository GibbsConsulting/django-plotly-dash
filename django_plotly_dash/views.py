from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse

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
    return app.augment_initial_layout(resp)

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
        argMap = {'id':id,
                  'session':request.session}
        resp = app.dispatch_with_args(rb, argMap)

    return HttpResponse(resp.data,
                        content_type=resp.mimetype)

def main_view(request, id, stateless=False, **kwargs):
    da, app = DashApp.locate_item(id, stateless)

    mFunc = app.locate_endpoint_function()
    resp = mFunc()
    return HttpResponse(resp)

