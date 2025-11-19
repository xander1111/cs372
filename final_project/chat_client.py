import sys
import socket
import threading

from chatui import init_windows, read_command, print_message, end_windows
from utils import send_packet, get_packet_data

def send_hello(socket, nick):
    packet = {
        "type": "hello",
        "nick": nick
    }
    send_packet(socket, packet)

def server_listener(socket, nick):
    buffer = b''
    while True:
        packet = get_packet_data(socket, buffer)
                
        if packet["type"] == "join":
            print_message(f"*** {packet["nick"]} has joined the chat")
        elif packet["type"] == "leave":
            print_message(f"*** {packet["nick"]} has left the chat")
        elif packet["type"] == "chat":
            print_message(f"{packet["nick"]}: {packet["message"]}")
        elif packet["type"] == "direct_chat":
            print_message(f"{packet["from"]} -> {packet["to"]}: {packet["message"]}")
        elif packet["type"] == "error":
            print_message(f"*** Server Error >> {packet["message"]}")

def keyboard_listener(socket, nick):
    running = True
    
    while running:
        message = read_command(f"{nick}> ")
        
        if message.startswith("/"):
            if message.startswith("/q"):
                running = False
            elif message.startswith("/message") or message.startswith("/msg"):
                if len(message.split(" ")) >= 3:
                    packet = {
                        "type": "direct_chat",
                        "to": message.split(" ")[1],
                        "message": message.split(" ", 2)[2]
                    }
                    send_packet(socket, packet)
                
        else:
            packet = {
                "type": "chat",
                "message": message
            }
            
            send_packet(socket, packet)

def run_client(host, port, nick):
    init_windows()
    
    s = socket.socket()
    s.connect((host, port))
    
    send_hello(s, nick)
    
    server_listener_thread = threading.Thread(target=server_listener, args=(s, nick), daemon=True)
    keyboard_listener_thread = threading.Thread(target=keyboard_listener, args=(s, nick), daemon=True)
    
    server_listener_thread.start()
    keyboard_listener_thread.start()
    
    keyboard_listener_thread.join()
    # server_listener_thread is set to be a daemon, so we shouldn't have to join it
    
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
