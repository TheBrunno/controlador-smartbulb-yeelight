import socket
import json

class BulbController:
    def __init__(self, ip, port):
        self.ip = ip
        self.port = port
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM) #TCP

    def turn_on(self, mode):
        cmd = {
            "id": 1,
            "method": "set_power",
            "params": ["on", mode, 500]
        }

        msg = (json.dumps(cmd) + "\r\n").encode()
         
        self.socket.connect((self.ip, self.port))
        self.socket.send(msg)

        self.socket.recv(1024)
        self.socket.close()

    def turn_off(self, mode):
        cmd = {
            "id": 1,
            "method": "set_power",
            "params": ["off", mode, 500]
        }

        msg = (json.dumps(cmd) + "\r\n").encode()

        self.socket.connect((self.ip, self.port))
        self.socket.send(msg)
        
        self.socket.recv(1024)
        self.socket.close()

    def toggle(self):
        cmd = {
            "id": 1,
            "method": "toggle",
            "params": []
        }

        msg = (json.dumps(cmd) + "\r\n").encode()

        self.socket.connect((self.ip, self.port))
        self.socket.send(msg)

        self.socket.recv(1024)
        self.socket.close()