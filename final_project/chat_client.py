import sys
import socket
import threading
import json

from chatui import init_windows, read_command, print_message, end_windows
from utils import broadcast_packet, get_packet_data

def send_hello(socket, nick):
    packet = {
        "type": "hello",
        "nick": nick
    }
    broadcast_packet(socket, packet)

def server_listener(socket):
    buffer = b''
    while True:
        packet = get_packet_data(socket, buffer)
                
        if packet["type"] == "join":
            print_message(f"*** {packet["nick"]} has joined the chat")
        elif packet["type"] == "leave":
            print_message(f"*** {packet["nick"]} has left the chat")
        elif packet["type"] == "chat":
            print_message(f"{packet["nick"]}> {packet["message"]}")

def keyboard_listener(socket, nick):
    while True:
        message = read_command(f"{nick}> ")
        
        # TODO add /q command
        
        packet = {
            "type": "chat",
            "message": message
        }
        
        broadcast_packet(socket, packet)

def run_client(host, port, nick):
    init_windows()
    
    s = socket.socket()
    s.connect((host, port))
    
    send_hello(s, nick)
    
    server_listener_thread = threading.Thread(target=server_listener, args=(s,), daemon=True)
    keyboard_listener_thread = threading.Thread(target=keyboard_listener, args=(s, nick), daemon=True)
    
    server_listener_thread.start()
    keyboard_listener_thread.start()
    
    keyboard_listener_thread.join()
    # server_listener_thread is set to daemon, so we shouldn't have to join it
    
    end_windows()
    
    exit()
    

def usage():
    print("usage: chat_client.py nick host port", file=sys.stderr)

def main(argv):
    try:
        nick = argv[1]
        host = argv[2]
        port = int(argv[3])
    except:
        usage()
        return 1

    run_client(host, port, nick)


if __name__ == "__main__":
    sys.exit(main(sys.argv))
