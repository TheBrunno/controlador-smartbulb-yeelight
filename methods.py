import json
import socket
from typing import Any


class BulbController:
    def __init__(self, ip: str, port: int, default_transition: int = 500):
        self.ip = ip
        self.port = port
        self.default_transition = default_transition

    def set_default_transition(self, milliseconds: int) -> None:
        self.default_transition = max(30, int(milliseconds))

    def send_params(self, payload: dict[str, Any], expect_response: bool = True) -> dict[str, Any] | None:
        raw = (json.dumps(payload) + "\r\n").encode()

        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.settimeout(2)
            sock.connect((self.ip, self.port))
            sock.sendall(raw)

            if not expect_response:
                return None

            response = sock.recv(4096).decode(errors="ignore").strip()

        if not response:
            return None

        try:
            return json.loads(response)
        except json.JSONDecodeError:
            return {"raw": response}

    def turn_on(self, mode: str = "smooth"):
        cmd = {"id": 1, "method": "set_power", "params": ["on", mode, self.default_transition]}
        return self.send_params(cmd)

    def turn_off(self, mode: str = "smooth"):
        cmd = {"id": 1, "method": "set_power", "params": ["off", mode, self.default_transition]}
        return self.send_params(cmd)

    def toggle(self):
        cmd = {"id": 1, "method": "toggle", "params": []}
        return self.send_params(cmd)

    def set_bright(self, percentage: int, mode: str = "smooth"):
        percentage = max(1, min(100, int(percentage)))
        cmd = {"id": 1, "method": "set_bright", "params": [percentage, mode, self.default_transition]}
        return self.send_params(cmd)

    def set_rgb(self, rgb: tuple[int, int, int], mode: str = "smooth"):
        r, g, b = [max(0, min(255, int(v))) for v in rgb]
        rgb_decimal = (r * 65536) + (g * 256) + b

        cmd = {"id": 1, "method": "set_rgb", "params": [rgb_decimal, mode, self.default_transition]}
        return self.send_params(cmd)

    def set_ct_abx(self, kelvin: int, mode: str = "smooth"):
        kelvin = max(1700, min(6500, int(kelvin)))
        cmd = {"id": 1, "method": "set_ct_abx", "params": [kelvin, mode, self.default_transition]}
        return self.send_params(cmd)

    def get_properties(self, properties: list[str] | None = None):
        if properties is None:
            properties = ["power", "bright", "ct", "rgb", "name"]
        cmd = {"id": 1, "method": "get_prop", "params": properties}
        return self.send_params(cmd)
