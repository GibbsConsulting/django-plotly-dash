'''
Utility functions

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
import json
import uuid


from _plotly_utils.optional_imports import get_module


from django.conf import settings
from django.core.cache import cache
from django.utils.module_loading import import_string

from django_plotly_dash._patches import DjangoPlotlyJSONEncoder


def _get_settings():
    try:
        the_settings = settings.PLOTLY_DASH
    except AttributeError:
        the_settings = None

    return the_settings if the_settings else {}

def pipe_ws_endpoint_name():
    'Return the endpoint for pipe websocket connections'
    return _get_settings().get('ws_route', 'dpd/ws/channel')

def dpd_http_endpoint_root():
    'Return the root of the http endpoint for direct insertion of pipe messages'
    return _get_settings().get('http_route', 'dpd/views')

def http_endpoint(stem):
    'Form the http endpoint for a specific stem'
    return "^%s/%s/$" % (dpd_http_endpoint_root(), stem)

def insert_demo_migrations():
    'Check settings and report if objects for demo purposes should be inserted during migration'

    return _get_settings().get('insert_demo_migrations', False)

def http_poke_endpoint_enabled():
    'Return true if the http endpoint is enabled through the settings'
    return _get_settings().get('http_poke_enabled', True)

def cache_timeout_initial_arguments():
    'Return cache timeout, in seconds, for initial arguments'
    return _get_settings().get('cache_timeout_initial_arguments', 60)

def initial_argument_location():
    'Return True if cache to be used for setting and getting initial arguments, or False for a session'

    setget_location = _get_settings().get('cache_arguments', True)

    return setget_location

def store_initial_arguments(request, initial_arguments=None):
    'Store initial arguments, if any, and return a cache identifier'

    if initial_arguments is None:
        return None

    # convert to dict is json string
    if isinstance(initial_arguments, str):
        initial_arguments = json.loads(initial_arguments)

    # Generate a cache id
    cache_id = "dpd-initial-args-%s" % str(uuid.uuid4()).replace('-', '')

    # Store args in json form in cache
    if initial_argument_location():
        cache.set(cache_id, initial_arguments, cache_timeout_initial_arguments())
    else:
        request.session[cache_id] = initial_arguments

    return cache_id

def get_initial_arguments(request, cache_id=None):
    'Extract initial arguments for the dash app'

    if cache_id is None:
        return None

    if initial_argument_location():
        return cache.get(cache_id)

    return request.session[cache_id]

def static_asset_root():
    return _get_settings().get('static_asset_root','dpd/assets')

def full_asset_path(module_name, asset_path):
    path_contrib = "%s/%s/%s" %(static_asset_root(),
                                "/".join(module_name.split(".")),
                                asset_path)
    return path_contrib

def static_asset_path(module_name, asset_path):
    return static_path(full_asset_path(module_name, asset_path))

def serve_locally():
    return _get_settings().get('serve_locally', False)

def static_path(relative_path):
    try:
        static_url = settings.STATIC_URL
    except:
        static_url = '/static/'
    return "%s%s" %(static_url, relative_path)

def stateless_app_lookup_hook():
    'Return a function that performs lookup for aa stateless app, given its name, or returns None'

    func_name = _get_settings().get('stateless_loader', None)
    if func_name:
        func = import_string(func_name)
        return func

    # Default is no additional lookup
    return lambda _: None


