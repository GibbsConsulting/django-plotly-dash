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

from django.conf import settings

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
