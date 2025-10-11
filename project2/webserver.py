import socket
import sys
import os
import mimetypes


def send_file(filepath, filetype, socket):
    try:
        with open(filepath, "rb") as fp:
            data = fp.read()   # Read entire file
            
            socket.sendall(f"\
HTTP/1.1 200 OK\r\n\
Content-Type: {filetype}\r\n\
Content-Length: {len(data)}\r\n\
Connection: close\r\n\
\r\n"\
            .encode("ISO-8859-1") + data)

    except:
        # File not found or other error
        socket.sendall("\
HTTP/1.1 404 Not Found\r\n\
Content-Type: text/plain\r\n\
Content-Length: 13\r\n\
Connection: close\r\n\
\r\n\
404 not found"\
            .encode("ISO-8859-1"))


if len(sys.argv) > 1:
    port = int(sys.argv[1])
else:
    port = 28333


s = socket.socket()
s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

s.bind(('', port))
s.listen()

print("Server started on port", port)

while True:
    connection = s.accept()
    connection_socket = connection[0]
    print(connection)
    print()
    req = ''
    while "\r\n\r\n" not in req:
        req += connection_socket.recv(4096).decode("ISO-8859-1")
    
    print(req)
    
    req_lines = req.split("\r\n")
    
    req_path = req_lines[0].split()[1]
    
    file_name = os.path.split(req_path)[-1]
    file_ext = os.path.splitext(file_name)[-1]
    file_type = mimetypes.guess_type(file_name)[0]
    
    send_file("./" + file_name, file_type, connection_socket)
    
    connection_socket.close()


s.close()
