from channels.generic.websocket import WebsocketConsumer

class MessageConsumer(WebsocketConsumer):
    def connect(self):
        self.accept()
    def disconnect(self, close_code):
        pass
    def receive(self, text_data):
        print("Got incoming")
        print(text_data)
        self.send("Thanks for [%s]"%text_data)
