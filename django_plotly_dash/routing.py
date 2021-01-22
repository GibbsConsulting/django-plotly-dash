'''
Routing for standard pipe connections

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

from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
from channels.http import AsgiHandler

from django.conf.urls import url
from django.urls import re_path

from .consumers import MessageConsumer, PokePipeConsumer
from .util import pipe_ws_endpoint_name, http_endpoint, http_poke_endpoint_enabled

# TODO document this and discuss embedding with other routes

http_routes = [
    ]

if http_poke_endpoint_enabled():
    http_routes.append(re_path(http_endpoint("poke"), PokePipeConsumer))

http_routes.append(re_path("^", AsgiHandler)) # AsgiHandler is 'the normal Django view handlers'

application = ProtocolTypeRouter({
    'websocket': AuthMiddlewareStack(URLRouter([re_path(pipe_ws_endpoint_name(), MessageConsumer),])),
    'http': AuthMiddlewareStack(URLRouter(http_routes)),
    })
