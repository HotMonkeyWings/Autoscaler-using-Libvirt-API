# This code is supposed to be used in the server (VM)
# It is called on boot

import socket
import math
import multiprocessing


def process_requests(s):
    while 1:
        try:
            # Receive and decode the message
            data, addr = s.recvfrom(1024)
            msg = data.decode()
            values, timer = msg.split()
            value = int(value)

            # Do complex mathematics
            value = (value + 2.301) * 3.45362 / 1.2321 * 33.123125
            value = (value % 1021) + 2.5435 + 3.555555555555 * 3.6634636 * 9.123123
            value = value % 1021
            print(f'{value}: Sent at {timer}')

            # Send msg and timer indicating when it was sent
            send_msg = str(value) + " " + timer
            s.sendto(send_msg.encode(), addr)
        except OverflowError:
            continue
        except ValueError:
            s.close()
            exit(0)

if __name__ == '__main__':
    # Initialize socket
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    port = 12345
    s.bind(('', port))

    # Start 5 Processes to receive and send requests
    proc = None
    for i in range(5):
        proc = multiprocessing.Process(target=process_requests, args=(s,))
        proc.start()
    proc.join()