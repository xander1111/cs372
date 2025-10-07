import socket
import sys


if len(sys.argv) > 1:
    domain = sys.argv[1]
else:
    domain = "example.com"

if len(sys.argv) > 2:
    port = int(sys.argv[2])
else:
    port = 80


s = socket.socket()

s.connect((domain, port))

s.sendall(f"\
GET / HTTP/1.1\r\n\
Host: {domain}\r\n\
Connection: close\r\n\r\n"\
    .encode("ISO-8859-1"))

while True:
    d = s.recv(4096)
    if len(d) == 0:
        break
    print(d.decode())

s.close()
