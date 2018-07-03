'''
Utility functions
'''

from django.conf import settings

try:
    ws_route = settings.PLOTLY_DASH.get('ws_route','ws/channel')
except:
    ws_route = "ws/channel"

def pipe_ws_endpoint_name():
    return ws_route

