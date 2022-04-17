# This code is supposed to be used in the server (VM)
# It is called on boot

import socket
import math

s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
port = 12345

s.bind(('', port))

while 1:
    try:
        data, addr = s.recvfrom(1024)
        value = int(data.decode())
        value = (value + 2.301) * 3.45362 / 1.2321 * 33.123125
        value = (value % 1021) + 2.5435 + 3.555555555555 * 3.6634636 * 9.123123
        value = value % 1021
        print(value)
    except OverflowError:
        continue
    except ValueError:
        s.close()
        exit(0)