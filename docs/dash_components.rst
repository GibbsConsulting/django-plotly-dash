.. _dash_components:

Dash components
===============

The ``dpd-components`` package contains ``Dash`` components. This package is installed as a
dependency of ``django-plotly-dash``.

.. _pipe_component:
The ``Pipe`` component
----------------------

Each ``Pipe`` component instance listens for messages on a single channel. The ``value`` member of any message on that channel whose ``label`` matches
that of the component will be used to update the ``value`` property of the component. This property can then be used in callbacks like
any other ``Dash`` component property.

An example, from the demo application:

.. code-block:: python

    import dpd_components as dpd

    app.layout = html.Div([
        ...
        dpd.Pipe(id="named_count_pipe",               # ID in callback
                 value=None,                          # Initial value prior to any message
                 label="named_counts",                # Label used to identify relevant messages
                 channel_name="live_button_counter"), # Channel whose messages are to be examined
        ...
        ])

The ``value`` of the message is sent from the server to all front ends with ``Pipe`` components listening
on the given ``channel_name``. This means that this part of the message should be small, and it must
be JSON serialisable. Also, there is no guarantee that any callbacks will be executed in the same Python
process as the one that initiated the initial message from server to front end.

The ``Pipe`` properties can be persisted like any other ``DashApp`` instance, although it is unlikely
that continued persistence of state on each update of this component is likely to be useful.

This component requires a bidirectional connection, such as a websocket, to the server. Inserting
a ``plotly_message_pipe`` :ref:`template tag <plotly_message_pipe>` is sufficient.
