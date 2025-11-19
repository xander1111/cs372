import socket
import sys
import select
import json

HEADER_LEN = 2

def packet_complete(data):
    if len(data) < 2:
        return False
    
    return len(data) >= (int.from_bytes(data[:HEADER_LEN], "big") + HEADER_LEN)

def packet_extract(data):
    packet_len = int.from_bytes(data[:HEADER_LEN], "big") + HEADER_LEN
    
    return data[:packet_len], data[packet_len:]

def get_packet_raw(socket, buffer):
    while not packet_complete(buffer):
        buffer += socket.recv(512)
        if len(buffer) == 0:
            return None
        
    packet, buffer = packet_extract(buffer)
        
    return packet

def get_packet_data(socket, buffer):
    packet = get_packet_raw(socket, buffer)
    return json.loads(packet[HEADER_LEN:])

def broadcast_packet(sockets, packet):
    packet = json.dumps(packet).encode()
    
    for s in sockets.keys():
        s.send(packet)

def broadcast_chat(sockets, message, nick):
    packet = {
        "type": "chat",
        "nick": nick,
        "message": message
    }
    broadcast_packet(sockets, packet)

def broadcast_join(sockets, nick):
    packet = {
        "type": "join",
        "nick": nick
    }
    broadcast_packet(sockets, packet)


def broadcast_dc(sockets, nick):
    packet = {
        "type": "leave",
        "nick": nick
    }
    broadcast_packet(sockets, packet)

def handle_packet(sockets, socket_from, nicks, packet):
    if packet["type"] == "hello":
        nick = packet["nick"]
        nicks[socket_from] = nick
        broadcast_join(sockets, nick)
    if packet["type"] == "chat":
        message = packet["message"]
        nick = nicks[socket_from]
        broadcast_chat(sockets, message, nick)

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
                    broadcast_dc(sockets, nicks[s])
                    
                else:
                    handle_packet(sockets, s, nicks, packet)


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
