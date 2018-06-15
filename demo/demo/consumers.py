from channels.generic.websocket import WebsocketConsumer

import json

class MessageConsumer(WebsocketConsumer):

    def connect(self):
        self.accept()

    def disconnect(self, close_code):
        pass

    def send_to_widgets(self, channel_name, label, value):
        self.send(json.dumps({'channel_name':channel_name,
                              'label':label,
                              'value':value}))
    def receive(self, text_data):
        print("Got incoming")
        message = json.loads(text_data)
        print(text_data)
        self.send(json.dumps({'message':"Thanks for [%s]"%text_data}))
        self.send(json.dumps({'original_message':message}))

        # TODO if type is connection_triplet then store and/or update the info
        # TODO else do something appropriate with the message

        channel_name = message.get('channel_name',"UNNAMED_CHANNEL")
        uid = message.get('uid',"0000-0000")
        label = message.get('label','DEFAULT$LABEL')

        self.send_to_widgets(channel_name=channel_name,
                             label=label,
                             value=uid)
