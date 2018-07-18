'''
Utility functions
'''

from django.conf import settings

def _get_settings():
    pd_settings = settings.PLOTLY_DASH
    return pd_settings if pd_settings else {}

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
