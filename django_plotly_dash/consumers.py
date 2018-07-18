'Define pipe consumer and also http endpoint for direct injection of pipe messages'

import json

from channels.generic.websocket import WebsocketConsumer
from channels.generic.http import AsyncHttpConsumer
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync

def _form_pipe_channel_name(channel_name):
    return "dpd_pipe_%s" % channel_name

def send_to_pipe_channel(channel_name,
                         label,
                         value):
    'Send message through pipe to client component'
    async_to_sync(async_send_to_pipe_channel)(channel_name=channel_name,
                                              label=label,
                                              value=value)

async def async_send_to_pipe_channel(channel_name,
                                     label,
                                     value):
    'Send message asynchronously through pipe to client component'
    pcn = _form_pipe_channel_name(channel_name)

    channel_layer = get_channel_layer()
    await channel_layer.group_send(pcn,
                                   {"type":"pipe.value",
                                    "label":label,
                                    "value":value})

class MessageConsumer(WebsocketConsumer):
    'Websocket handler for pipe to dash component'
    def __init__(self, *args, **kwargs):
        super(MessageConsumer, self).__init__(*args, **kwargs)

        self.channel_maps = {}

    def connect(self):
        self.accept()

    def disconnect(self, reason):  # pylint: disable=arguments-differ

        for _, pipe_group_name in self.channel_maps.items():
            async_to_sync(self.channel_layer.group_discard)(pipe_group_name, self.channel_name)

        return super(MessageConsumer, self).disconnect(reason)

    def pipe_value(self, message):
        'Send a new value into the ws pipe'
        jmsg = json.dumps(message)
        self.send(jmsg)

    def update_pipe_channel(self, uid, channel_name, label): # pylint: disable=unused-argument
        '''
        Update this consumer to listen on channel_name for the js widget associated with uid
        '''
        pipe_group_name = _form_pipe_channel_name(channel_name)

        if self.channel_layer:
            current = self.channel_maps.get(uid, None)
            if current != pipe_group_name:
                if current:
                    async_to_sync(self.channel_layer.group_discard)(current, self.channel_name)

                self.channel_maps[uid] = pipe_group_name
                async_to_sync(self.channel_layer.group_add)(pipe_group_name, self.channel_name)

    def receive(self, text_data): # pylint: disable=arguments-differ
        message = json.loads(text_data)

        message_type = message.get('type', 'unknown_type')
        if message_type == 'connection_triplet':

            try:
                channel_name = message['channel_name']
                uid = message['uid']
                label = message['label']

                self.update_pipe_channel(uid, channel_name, label)

            except: # pylint: disable=bare-except
                # Ignore malformed message
                # TODO enable logging of this sort of thing
                pass

        else:
            # Not a periodic control message, so do something useful
            # For now, this is just pushing to all other pipe consumers indiscrimnately
            # TODO grab defaults from settings if present

            channel_name = message.get('channel_name', "UNNAMED_CHANNEL")
            value = message.get('value', None)
            label = message.get('label', 'DEFAULT$LABEL')

            send_to_pipe_channel(channel_name=channel_name,
                                 label=label,
                                 value=value)

class PokePipeConsumer(AsyncHttpConsumer):
    'Async handling of http request inserting pipe message'

    async def handle(self, body):

        user = self.scope.get('user', None)
        as_utf = body.decode('utf-8')
        try:
            incoming_message = json.loads(as_utf)

            # Get label value and channel_name out of the body
            channel_name = incoming_message.get('channel_name', 'UNNAMED_CHANNEL')
            value = incoming_message.get("value", None)
            label = incoming_message.get("label", "DEFAULT$LABEL")

            # TODO Use user info (and also csrf and other checks as desired) to prevent misuse
            await async_send_to_pipe_channel(channel_name,
                                             label,
                                             value)

            response = """PokePipeConsumer consumed message of %s for %s
""" %(incoming_message, user)
            response_code = 200

        except: # pylint: disable=bare-except

            response = """Unable to understand and forward on message of %s
""" % as_utf
            response_code = 500

        await self.send_response(response_code,
                                 response.encode('utf-8'))
