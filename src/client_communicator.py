import socket
s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
s.sendto('3'.encode(), ('', 8000))