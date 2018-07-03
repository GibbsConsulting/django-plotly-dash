from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack

from django.conf.urls import url

from django_plotly_dash.consumers import MessageConsumer
from django_plotly_dash.util import pipe_ws_endpoint_name

application = ProtocolTypeRouter({
    'websocket': AuthMiddlewareStack(URLRouter([url(pipe_ws_endpoint_name(), MessageConsumer),])),
    })
