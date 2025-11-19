import sys
import socket
import threading

from chatui import init_windows, read_command, print_message, end_windows
from utils import send_packet, get_packet_data

running = True
forced_close = False

def handle_packet(socket, buffer):
    global running
    global forced_close
    
    packet = get_packet_data(socket, buffer)
                
    if packet is None:
        print_message("*** The connection with the server has been closed")
        running = False
        forced_close = True
        return packet
    
    elif packet["type"] == "close":
        print_message("*** The server has closed your connection for the following reason:")
        print_message(packet["message"])
        running = False
        forced_close = True
        return packet
            
    elif packet["type"] == "join":
        print_message(f"*** {packet["nick"]} has joined the chat")
        
    elif packet["type"] == "leave":
        print_message(f"*** {packet["nick"]} has left the chat")
        
    elif packet["type"] == "chat":
        print_message(f"{packet["nick"]}: {packet["message"]}")
        
    elif packet["type"] == "direct_chat":
        print_message(f"{packet["from"]} -> {packet["to"]}: {packet["message"]}")
        
    elif packet["type"] == "error":
        print_message(f"*** Server Error >> {packet["message"]}")
        
    elif packet["type"] == "list":
        print_message(f"*** Currently Connected Users >> {", ".join(packet["message"])}")
        
    elif packet["type"] == "me":
        print_message(f"[{" ".join((packet["nick"], packet["message"]))}]")
        
    return packet

def send_hello(socket, nick):
    global running
    
    packet = {
        "type": "hello",
        "nick": nick
    }
    send_packet(socket, packet)
    
    buffer = b''
    packet = {"type": None, "message": None}
    while packet is not None and packet["type"] != "join" and packet["message"] != nick:
        packet = handle_packet(socket, buffer)  # We should either receive a packet with the user's join message, or a connection close if the nickname is taken

def server_listener(socket):
    global running
    
    buffer = b''
    while running:
        handle_packet(socket, buffer)

def handle_command(socket, command):
    global running
    
    if command.startswith("/q"):
        running = False
    elif command.startswith("/message") or command.startswith("/msg"):
        if len(command.split(" ")) >= 3:
            packet = {
                "type": "direct_chat",
                "to": command.split(" ")[1],
                "message": command.split(" ", 2)[2]
            }
            send_packet(socket, packet)
    elif command.startswith("/list") or command.startswith("/l"):
        packet = {
            "type": "list"
        }
        send_packet(socket, packet)
    elif command.startswith("/me"):
        if len(command.split(" ")) >= 2:
            packet = {
                "type": "me",
                "message": command.split(" ", 1)[1]
            }
            send_packet(socket, packet)

def keyboard_listener(socket, nick):
    global running
    
    while running:
        message = read_command(f"{nick}> ")
        
        if message.startswith("/"):
            handle_command(socket, message)
        else:
            packet = {
                "type": "chat",
                "message": message
            }
            
            send_packet(socket, packet)

def run_client(host, port, nick):
    global running
    
    init_windows()
    
    s = socket.socket()
    s.connect((host, port))
    
    send_hello(s, nick)
    
    if not running and forced_close:
        read_command("Press enter to continue")
        end_windows()
        return
    
    server_listener_thread = threading.Thread(target=server_listener, args=(s,), daemon=True)
    keyboard_listener_thread = threading.Thread(target=keyboard_listener, args=(s, nick), daemon=True)
    
    server_listener_thread.start()
    keyboard_listener_thread.start()
    
    keyboard_listener_thread.join()
    keyboard_listener_thread.join()
    
    if forced_close:
        read_command("Press enter to continue")
    
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
