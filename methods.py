import socket
import json

class BulbController:
    def __init__(self, ip:str, port:int, default_transition:int=0):
        self.ip = ip
        self.port = port
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM) #TCP
        self.default_transition = default_transition

    def send_params(self, params):
        params = (json.dumps(params) + "\r\n").encode()

        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.connect((self.ip, self.port))
            sock.send(params)
            sock.recv(1024)

    def turn_on(self, mode="smooth"):
        cmd = {
            "id": 1,
            "method": "set_power",
            "params": ["on", mode, self.default_transition]
        }
        self.send_params(cmd)

    def turn_off(self, mode="smooth"):
        cmd = {
            "id": 1,
            "method": "set_power",
            "params": ["off", mode, self.default_transition]
        }
        self.send_params(cmd)


    def toggle(self):
        cmd = {
            "id": 1,
            "method": "toggle",
            "params": []
        }
        self.send_params(cmd)


    def set_bright(self, percentage:int, mode:str="smooth"):
        cmd = {
            "id": 1,
            "method": "set_bright",
            "params": [percentage, mode, self.default_transition]
        }
        self.send_params(cmd)

    def set_bright(self, percentage:int, mode:str="smooth"):
        cmd = {
            "id": 1,
            "method": "set_bright",
            "params": [percentage, mode, self.default_transition]
        }
        self.send_params(cmd)

    def set_rgb(self, rgb:tuple, mode:str="smooth"):
        rgb_decimal = (rgb[0]*65536)+(rgb[1]*256)+rgb[2]

        cmd = {
            "id": 1,
            "method": "set_rgb",
            "params": [rgb_decimal, mode, self.default_transition]
        }
        self.send_params(cmd)

    def set_ct_abx(self, kelvin:int, mode:str="smooth"):
        cmd = {
            "id": 1,
            "method": "set_ct_abx",
            "params": [kelvin, mode, self.default_transition]
        }
        self.send_params(cmd)