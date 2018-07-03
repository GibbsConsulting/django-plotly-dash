from channels.generic.websocket import WebsocketConsumer

import json

ALL_CONSUMERS = []

class MessageConsumer(WebsocketConsumer):
    def __init__(self, *args, **kwargs):
        super(MessageConsumer, self).__init__(*args, **kwargs)
        global ALL_CONSUMERS
        ALL_CONSUMERS.append(self)

        print("Creating a MessageConsumer")
        print(len(ALL_CONSUMERS))

        self.callcount = 0

    def connect(self):
        self.accept()

    def disconnect(self, close_code):
        ac = []
        global ALL_CONSUMERS
        for c in ALL_CONSUMERS:
            if c != self:
                ac.append(c)
        ALL_CONSUMERS = ac
        return super(MessageConsumer, self).disconnect(close_code)

    def send_to_widgets(self, channel_name, label, value):
        message = json.dumps({'channel_name':channel_name,
                              'label':label,
                              'value':value})
        global ALL_CONSUMERS

        for c in ALL_CONSUMERS:
            c.send(message)

        if False:
            self.callcount += 1
            if self.callcount > 10:
                import gc
                print("Running collection")
                gc.collect()
                self.callcount = 0

            import objgraph
            objgraph.show_most_common_types()

    def receive(self, text_data):
        message = json.loads(text_data)

        message_type = message.get('type','unknown_type')

        if message_type == 'connection_triplet':

            channel_name = message.get('channel_name',"UNNAMED_CHANNEL")
            uid = message.get('uid',"0000-0000")
            label = message.get('label','DEFAULT$LABEL')

            # For now, send the uid as value. This essentially 'resets' the value
            # each time the periodic connection announcement is made
            self.send_to_widgets(channel_name=channel_name,
                                 label=label,
                                 value=uid)
        else:
            # Not a periodic control message, so do something useful
            # For now, this is just pushing to all other consumers indiscrimnately

            channel_name = message.get('channel_name',"UNNAMED_CHANNEL")
            uid = message.get('uid',"0000-0000")
            value = message.get('value',{'source_uid':uid})
            label = message.get('label','DEFAULT$LABEL')

            self.send_to_widgets(channel_name=channel_name,
                                 label=label,
                                 value=value)
