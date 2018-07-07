'''
Utility functions
'''

# pylint: disable=bare-except

from django.conf import settings

try:
    ws_route = settings.PLOTLY_DASH.get('ws_route', 'dpd/ws/channel')
except:
    ws_route = "dpd/ws/channel"

try:
    http_route = settings.PLOTLY_DASH.get('http_route', 'dpd/views')
except:
    http_route = "dpd/views"


def pipe_ws_endpoint_name():
    'Return the endpoint for pipe websocket connections'
    return ws_route

def dpd_http_endpoint_root():
    'Return the root of the http endpoint for direct insertion of pipe messages'
    return http_route

def http_endpoint(stem):
    'Form the http endpoint for a specific stem'
    return "^%s/%s/$" % (dpd_http_endpoint_root(), stem)
