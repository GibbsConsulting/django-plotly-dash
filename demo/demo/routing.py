from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack

from django.conf.urls import url

from .consumers import MessageConsumer

application = ProtocolTypeRouter({
    'websocket': AuthMiddlewareStack(URLRouter([url('ws/channel', MessageConsumer),])),
    })
