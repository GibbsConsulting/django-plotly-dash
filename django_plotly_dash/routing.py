'Routing for standard pipe connections'

from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
from channels.http import AsgiHandler

from django.conf.urls import url

from .consumers import MessageConsumer, PokePipeConsumer
from .util import pipe_ws_endpoint_name, http_endpoint

# TODO document this and discuss embedding with other routes
application = ProtocolTypeRouter({
    'websocket': AuthMiddlewareStack(URLRouter([url(pipe_ws_endpoint_name(), MessageConsumer),])),
    'http': AuthMiddlewareStack(URLRouter([url(http_endpoint("poke"), PokePipeConsumer),
                                           url("^", AsgiHandler),])), # AsgiHandler is 'the normal Django view handlers'
    })
