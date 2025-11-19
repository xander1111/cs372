import socket
import sys
import select

from utils import broadcast_packet, get_packet_data, send_packet

HEADER_LEN = 2

def broadcast_chat(sockets, listener, message, nick):
    packet = {
        "type": "chat",
        "nick": nick,
        "message": message
    }
    broadcast_packet(sockets, listener, packet)

def broadcast_join(sockets, listener, nick):
    packet = {
        "type": "join",
        "nick": nick
    }
    broadcast_packet(sockets, listener, packet)


def broadcast_dc(sockets, listener, nick):
    packet = {
        "type": "leave",
        "nick": nick
    }
    broadcast_packet(sockets, listener, packet)
    
def send_direct(socket_to, nick_from, nick_to, message):
    packet = {
        "type": "direct_chat",
        "from": nick_from,
        "to": nick_to,
        "message": message
    }
    send_packet(socket_to, packet)
    
def send_error(socket_to, message):
    packet = {
        "type": "error",
        "message": message
    }
    send_packet(socket_to, packet)

def handle_packet(sockets, listener, socket_from, nicks, packet):
    if packet["type"] == "hello":
        nick = packet["nick"]
        nicks[socket_from] = nick
        broadcast_join(sockets, listener, nick)
    elif packet["type"] == "chat":
        message = packet["message"]
        nick = nicks[socket_from]
        broadcast_chat(sockets, listener, message, nick)
    elif packet["type"] == "direct_chat":
        message = packet["message"]
        nick_from = nicks[socket_from]
        nick_to = packet["to"]
        try:
            socket_to = {value: key for key, value in nicks.items()}[nick_to]
            send_direct(socket_to, nick_from, nick_to, message)
            send_direct(socket_from, nick_from, nick_to, message)
        except:
            send_error(socket_from, f"User {nick_to} not found")

def run_server(port):
    listener = socket.socket()
    listener.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    
    listener.bind(("localhost", port))
    
    listener.listen()
    
    sockets = {}
    sockets[listener] = b''
    
    nicks = {}
    
    while True:
        ready, _, _ = select.select(sockets.keys(), {}, {})
        
        for s in ready:
            if s is listener:
                client_socket, _ = s.accept()
                sockets[client_socket] = b''
                
            else:
                packet = get_packet_data(s, sockets[s])
                
                if packet is None:
                    del sockets[s]
                    broadcast_dc(sockets, listener, nicks[s])
                    
                else:
                    handle_packet(sockets, listener, s, nicks, packet)


def usage():
    print("usage: chat_server.py port", file=sys.stderr)

def main(argv):
    try:
        port = int(argv[1])
    except:
        usage()
        return 1

    run_server(port)

if __name__ == "__main__":
    sys.exit(main(sys.argv))
