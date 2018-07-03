from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack

from django.conf.urls import url

from .consumers import MessageConsumer
from .util import pipe_ws_endpoint_name

application = ProtocolTypeRouter({
    'websocket': AuthMiddlewareStack(URLRouter([url(pipe_ws_endpoint_name(), MessageConsumer),])),
    })
