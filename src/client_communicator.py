import socket, signal

from extra_utils import clearConsole, signal_handler
from configs import DELAY_CONFIG

if __name__ == "__main__":
    signal.signal(signal.SIGINT, signal_handler)
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    option = None

    while 1:
        clearConsole()
        print('[CTRL + C] to Terminate.\n\n')
        if option: 
            print("Current Request Traffic: ", DELAY_CONFIG[int(option)][0])
        option = input("""1. Low
2. Medium
3. High
Change Load: """)
        s.sendto(option.encode(), ('', 8000))