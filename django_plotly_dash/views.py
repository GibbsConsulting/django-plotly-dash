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

import re

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

    # EB added
    print("main_view: checking if bool is true")
    if request.session.get('create_dash_html') == True:
        print("main_view: creating content")

        # build the base url and use for redirecting to the appropriate url:
        dpd_app_url = request.build_absolute_uri()
        split_url = dpd_app_url.split('/')
        end_index = [i for i, j in enumerate(split_url) if j == 'django_plotly_dash'][0]
        print("end_index: " + str(end_index))
        base_url = "/".join(split_url[:end_index])
        print("base_url: " +str(base_url))
        print("app.dashboard_url: " +str(app.content_redirect_url))
        main_app_url = base_url + "/" + app.content_redirect_url
        print("Printing main_app_url: " + str(main_app_url))

        # Get the response value:
        dash_content = HttpResponse(resp).getvalue()

        # Remove unwanted content from the response
        dash_content = clean_dash_content(dash_content)

        # Store the dash content in the request session so that it can be injected in to a template
        request.session['dash_content'] = dash_content
        request.session['create_dash_html'] = False

        print("Redirecting to main app url")
        return HttpResponseRedirect(redirect_to=main_app_url)

    else: # else use the original method made by the dpd team
        return HttpResponse(resp)


        # End EB added



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


def create_Dash_html(request, dash_app):

    # If this is the first time loading the site, signal to create a Dash:
    if request.session.get('create_dash_html') == None:
        print("no dash created before. setting bool to True..")
        request.session['create_dash_html'] = True

    # if a Dash to is to be created
    if request.session['create_dash_html'] == True:
        print("reditrecting to dashh app base pathname to get content: %s" %(str(dash_app.get_base_pathname(specific_identifier=None)[1])))


        return HttpResponseRedirect(redirect_to=dash_app.get_base_pathname(specific_identifier=None)[1])

    else:
        # set the flag for the next time a Dash is to be created upon a page load
        request.session['create_dash_html'] = True
        return


def clean_dash_content(dash_content):
    '''Description: This is a total hack to get rid of carriage returns in the html returned by the call to dash_dispatcher.
    	  	    There is a more elegant way but I haven't sussed it yet.'''
    #print("Function: clean_dash_content")
    string_content = str(dash_content)
    string_content = string_content.replace("\\n   ", "")
    string_content = string_content.replace("\\\\n", "")
    string_content = string_content.replace("\\\'", "")
    string_content = string_content.replace(">\\n<", "><")
    string_content = string_content[:-6]
    string_content = string_content[1:]
    string_content = re.sub('\s+',' ', string_content)
    string_content = string_content[1:]
    cleaned_dash_content = string_content

    return cleaned_dash_content
