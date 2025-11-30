import socket
import re

MSEARCH_MSG = \
    'M-SEARCH * HTTP/1.1\r\n' \
    'HOST: 239.255.255.250:1982\r\n' \
    'MAN: "ssdp:discover"\r\n' \
    'ST: wifi_bulb\r\n' \
    '\r\n'

def discover_yeelight_bulbs(timeout=0.5):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.settimeout(timeout)
    sock.sendto(MSEARCH_MSG.encode(), ('239.255.255.250', 1982)) #UDP

    bulbs = []

    try:
        while True:
            data, addr = sock.recvfrom(65507)
            text = data.decode()

            m = re.search(r'Location: yeelight://(.+):(\d+)', text)
            if m:
                ip = m.group(1)
                port = int(m.group(2))
                bulbs.append((ip, port))
    except socket.timeout:
        pass

    return bulbs
