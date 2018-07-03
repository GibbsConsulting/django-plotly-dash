from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack

from django.conf.urls import url
from django.conf import settings

try:
    ws_route = settings.PLOTLY_DASH.get('ws_route','ws/channel')
except:
    ws_route = "ws/channel"

from .consumers import MessageConsumer

application = ProtocolTypeRouter({
    'websocket': AuthMiddlewareStack(URLRouter([url(ws_route, MessageConsumer),])),
    })
