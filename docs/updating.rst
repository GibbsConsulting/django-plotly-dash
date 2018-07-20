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

There is an HTTP endpoint that allows direct insertion of messages into a message channel.

Deployment
----------

Need redis and daphne.

