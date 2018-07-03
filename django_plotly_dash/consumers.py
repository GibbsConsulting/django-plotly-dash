from channels.generic.websocket import WebsocketConsumer
from channels.generic.http import AsyncHttpConsumer
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync

import json

def _form_pipe_channel_name( channel_name ):
    return "dpd_pipe_%s" % channel_name

def send_to_pipe_channel( channel_name,
                          label,
                          value ):
    async_to_sync(async_send_to_pipe_channel)(channel_name=channel_name,
                                              label=label,
                                              value=value)

async def async_send_to_pipe_channel( channel_name,
                                      label,
                                      value ):
    pcn = _form_pipe_channel_name(channel_name)

    channel_layer = get_channel_layer()
    await channel_layer.group_send(pcn,
                                   {"type":"pipe.value",
                                    "label":label,
                                    "value":value})

class MessageConsumer(WebsocketConsumer):
    def __init__(self, *args, **kwargs):
        super(MessageConsumer, self).__init__(*args, **kwargs)

        self.channel_maps = {}

    def connect(self):
        self.accept()

    def disconnect(self, close_code):

        for k, v in self.channel_maps.items():
            async_to_sync(self.channel_layer.group_discard)(v, self.channel_name)

        return super(MessageConsumer, self).disconnect(close_code)

    def pipe_value(self, message):
        jmsg = json.dumps(message)
        self.send(jmsg)

    def update_pipe_channel(self, uid, channel_name, label):
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
                print("Attaching %s to channel: %s" % (uid, pipe_group_name))
                async_to_sync(self.channel_layer.group_add)(pipe_group_name, self.channel_name)

    def receive(self, text_data):
        message = json.loads(text_data)

        message_type = message.get('type','unknown_type')
        if message_type == 'connection_triplet':

            try:
                channel_name = message['channel_name']
                uid = message['uid']
                label = message['label']

                self.update_pipe_channel(uid, channel_name, label)

                send_to_pipe_channel(channel_name,
                                     label,
                                     uid)

            except:
                # Ignore malformed message
                # TODO enable logging of this sort of thing
                pass

        else:
            # Not a periodic control message, so do something useful
            # For now, this is just pushing to all other pipe consumers indiscrimnately
            # TODO grab defaults from settings if present

            channel_name = message.get('channel_name',"UNNAMED_CHANNEL")
            value = message.get('value',None)
            label = message.get('label','DEFAULT$LABEL')

            send_to_pipe_channel(channel_name=channel_name,
                                 label=label,
                                 value=value)

class PokePipeConsumer(AsyncHttpConsumer):

    async def handle(self, body):
        print("Got a PipePoke")
        incoming_message = json.loads(body.decode("utf-8"))
        print(incoming_message)
        # Get label value and channel_name out of the body
        channel_name = incoming_message.get('channel_name','UNNAMED_CHANNEL')
        value = incoming_message.get("value", None)
        label = incoming_message.get("label","DEFAULT$LABEL")

        await async_send_to_pipe_channel(channel_name,
                                         label,
                                         value)

        await self.send_response(200,b"Response Bytes Here")
