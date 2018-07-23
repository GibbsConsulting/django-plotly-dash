.. _updating:

Live updating
=============

Live updating is supported using additional ``Dash`` :ref:`components <dash_components>` and
leveraging `Django Channels <https://channels.readthedocs.io/en/latest/>`_ to provide websocket endpoints.

Server-initiated messages are sent to all interested clients. The content of the message is then injected into
the application from the client, and from that point it is handled like any other value passed to a callback function.
The messages are constrained to be JSON serialisable, as that is how they are transmitted to and from the clients, and should
also be as small as possible given that they travel from the server, to each interested client, and then back to the
server again as an argument to one or more callback functions.

The round-trip of the message is a deliberate design choice, in order to enable the value within the message to be treated
as much as possible like any other piece of data within a ``Dash`` application. This data is essentially stored
on the client side of the client-server split, and passed to the server when each callback is invoked; note that this also
encourages designs that keep the size of in-application data small. An
alternative approach, such as directly invoking
a callback in the server, would require the server to maintain its own copy of the application state.

Live updating requires a server setup that is considerably more
complex than the alternative, namely use of the built-in `Interval <https://dash.plot.ly/live-updates>`_ component. However, live
updating can be used to reduce server load (as callbacks are only made when needed) and application latency (as callbacks are
invoked as needed, not on the tempo of the Interval component).

Message channels
----------------

Messages are passed through named channels, and each message consists
of a ``label`` and ``value`` pair. A :ref:`Pipe <pipe_component>` component is provided that listens for messages and makes
them available to ``Dash`` callbacks. Each message is sent through a message channel to all ``Pipe`` components that have
registered their interest in that channel, and in turn the components will select messages by ``label``.

A message channel exists as soon as a component signals that it is listening for messages on it. The
message delivery requirement is 'hopefully at least once'. In other words, applications should be robust against both the failure
of a message to be delivered, and also for a message to be delivered multiple times. A design approach that has messages
of the form 'you should look at X and see if something should be done' is strongly encouraged. The accompanying demo has
messages of the form 'button X at time T', for example.

Sending messages from within Django
-----------------------------------

Messages can be easily sent from within Django, provided that they are within the ASGI server.

.. code-block:: python

   from django_plotly_dash.consumers import send_to_pipe_channel

   # Send a message
   #
   # This function may return *before* the message has been sent
   # to the pipe channel.
   #
   send_to_pipe_channel(channel_name="live_button_counter",
                        label="named_counts",
                        value=value)

   # Send a message asynchronously
   #
   await async_send_to_pipe_channel(channel_name="live_button_counter",
                                    label="named_counts",
                                    value=value)

In general, making assumptions about the ordering of code between message sending and receiving is
unsafe. The ``send_to_pipe`` function uses the Django Channels ``async_to_sync`` wrapper around
a call to ``async_send_to_pipe`` and therefore may return before the asynchronous call is made (perhaps
on a different thread). Furthermore, the transit of the message through the channels backend
introduces another indeterminacy.

HTTP Endpoint
-------------

There is an HTTP endpoint, :ref:`configured <configuration>` with
the ``http_route`` option, that allows direct insertion of messages into a message
channel. It is a
direct equivalent of calling the ``send_to_pipe_channel`` function, and
expects the ``channel_name``, ``label`` and ``value`` arguments to be provided in a JSON-encoded
dictionary.

.. code-block:: bash

   curl -d '{"channel_name":"live_button_counter",
             "label":"named_counts",
             "value":{"click_colour":"cyan"}}'
             http://localhost:8000/dpd/views/poke/

This will cause the (JSON-encoded) ``value`` argument to be sent on the ``channel_name`` channel with
the given ``label``.

The provided endpoint skips any CSRF checks
and does not perform any security checks such as authentication or authorisation, and should
be regarded as a starting point for a more complete implementation if exposing this functionality is desired. On the
other hand, if this endpoint is restricted so that it is only available from trusted sources such as the server
itself, it does provide a mechanism for Django code running outside of the ASGI server, such as in a WSGI process or
Celery worker, to push a message out to running applications.

The ``http_poke_enabled`` flag controls the availability of the endpoint. If false, then it is not registered at all and
all requests will receive a 404 HTTP error code.

Deployment
----------

The live updating feature needs both Redis, as it is the only supported backend at present for v2.0 and up of
Channels, and Daphne or any other ASGI server for production use. It is also good practise to place the server(s) behind
a reverse proxy such as Nginx; this can then also be configured to serve Django's static files.

A further consideration is the use of a WSGI server, such as Gunicorn, to serve the non-asynchronous subset of the http
routes, albeit at the expense of having to separately manage ASGI and WSGI servers. This can be easily achieved through selective
routing at the reverse proxy level, and is the driver behind the ``ws_route`` configuration option.

In passing, note that the demo also uses Redis as the caching backend for Django.
