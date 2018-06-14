from channels.generic.websocket import WebsocketConsumer

import json

class MessageConsumer(WebsocketConsumer):
    def connect(self):
        self.accept()
    def disconnect(self, close_code):
        pass
    def receive(self, text_data):
        print("Got incoming")
        message = json.loads(text_data)
        print(text_data)
        self.send(json.dumps({'message':"Thanks for [%s]"%text_data}))
        self.send(json.dumps({'original_message':message}))
