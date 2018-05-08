from django.shortcuts import render

import flask
import json

from .dash_wrapper import get_app_instance_by_id
from django.http import HttpResponse

def routes(*args,**kwargs):
    pass

def dependencies(request, id, **kwargs):
    app = get_app_instance_by_id(id)
    with app.app_context():
        mFunc = app.locate_endpoint_function('dash-dependencies')
        resp = mFunc()
        return HttpResponse(resp.data,
                            content_type=resp.mimetype)

def layout(request, id, **kwargs):
    app = get_app_instance_by_id(id)
    mFunc = app.locate_endpoint_function('dash-layout')
    resp = mFunc()
    return HttpResponse(resp.data,
                        content_type=resp.mimetype)

def update(request, id, **kwargs):
    app = get_app_instance_by_id(id)
    mFunc = app.locate_endpoint_function('dash-update-component')
    # Fudge request object
    rb = json.loads(request.body.decode('utf-8'))
    with app.test_request_context():
        # inputs state and output needed in the json objects
        flask.request._cached_json = (rb, flask.request._cached_json[True])
        resp = mFunc()
    return HttpResponse(resp.data,
                        content_type=resp.mimetype)

def main_view(request, id, **kwargs):
    app = get_app_instance_by_id(id)
    mFunc = app.locate_endpoint_function()
    resp = mFunc()
    return HttpResponse(resp)

