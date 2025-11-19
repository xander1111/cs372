# Example usage:
#
# python select_server.py 3490

import sys
import socket
import select

def run_server(port):
    listener = socket.socket()
    listener.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    
    listener.bind(("localhost", port))
    
    listener.listen()
    
    sockets = set()
    sockets.add(listener)
    
    while True:
        ready, _, _ = select.select(sockets, {}, {})
        
        for s in ready:
            if s is listener:
                client_socket, client_addr = s.accept()
                sockets.add(client_socket)
                print(f"{client_addr}: connected")
            else:
                data = s.recv(1024)
                
                if len(data) == 0:
                    sockets.remove(s)
                    print(f"{s.getpeername()}: disconnected")
                    
                else:
                    print(f"{s.getpeername()} {len(data)} bytes: b'{data.decode()}'")


#--------------------------------#
# Do not modify below this line! #
#--------------------------------#

def usage():
    print("usage: select_server.py port", file=sys.stderr)

def main(argv):
    try:
        port = int(argv[1])
    except:
        usage()
        return 1

    run_server(port)

if __name__ == "__main__":
    sys.exit(main(sys.argv))
