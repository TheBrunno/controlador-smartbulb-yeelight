import re
import socket

MSEARCH_MSG = (
    "M-SEARCH * HTTP/1.1\r\n"
    "HOST: 239.255.255.250:1982\r\n"
    "MAN: \"ssdp:discover\"\r\n"
    "ST: wifi_bulb\r\n"
    "\r\n"
)


def discover_yeelight_bulbs(timeout: float = 1.0) -> list[tuple[str, int]]:
    bulbs: list[tuple[str, int]] = []
    seen: set[tuple[str, int]] = set()

    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
        sock.settimeout(timeout)
        sock.sendto(MSEARCH_MSG.encode(), ("239.255.255.250", 1982))  # UDP multicast

        try:
            while True:
                data, _ = sock.recvfrom(65507)
                text = data.decode(errors="ignore")

                match = re.search(r"Location:\s*yeelight://([^:]+):(\d+)", text, re.IGNORECASE)
                if match:
                    bulb = (match.group(1), int(match.group(2)))
                    if bulb not in seen:
                        seen.add(bulb)
                        bulbs.append(bulb)
        except socket.timeout:
            pass

    return bulbs
