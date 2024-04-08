
import socket

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect((socket.gethostname(), 9000))

while True:
    sent = s.send(b'0101010101')