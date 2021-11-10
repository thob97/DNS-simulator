import json

DATASIZE = 1024

class Socket():
    def __init__(self,socket,adress):
        self.socket = socket
        self.adress = adress

    def send_json(self, json_obj):
        self.socket.send(json.dumps(json_obj).encode('utf-8'))

    def recv_json(self):
        json_str = self.socket.recv(DATASIZE).decode('utf-8')
        return json.loads(json_str)