import socket
import sys


if len(sys.argv) > 1:
    port = int(sys.argv[1])
else:
    port = 28333

    
s = socket.socket()
s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

s.bind(('', port))
s.listen()

while True:
    connection = s.accept()
    connection_socket = connection[0]
    print(connection)
    print()
    d = ''
    while "\r\n\r\n" not in d:
        d = connection_socket.recv(4096).decode()
        print(d)
        
    connection_socket.sendall("\
HTTP/1.1 200 OK\r\n\
Content-Type: text/plain\r\n\
Content-Length: 6\r\n\
Connection: close\r\n\
\r\n\
Hello!\r\n"\
    .encode("ISO-8859-1"))
    
    connection_socket.close()


s.close()
