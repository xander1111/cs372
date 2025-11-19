import json

HEADER_LEN = 2

def packet_complete(data):
    if len(data) < 2:
        return False
    
    return len(data) >= (int.from_bytes(data[:HEADER_LEN], "big") + HEADER_LEN)

def packet_extract(data):
    packet_len = int.from_bytes(data[:HEADER_LEN], "big") + HEADER_LEN
    
    return data[:packet_len], data[packet_len:]

def get_packet_raw(s, buffer):
    while not packet_complete(buffer):
        buffer += s.recv(512)
        if len(buffer) == 0:
            return None
    
    packet, buffer = packet_extract(buffer)
        
    return packet

def get_packet_data(s, buffer):
    packet = get_packet_raw(s, buffer)
    if packet is None:
        return None
    return json.loads(packet[HEADER_LEN:])

def send_packet(s, packet):
    packet = json.dumps(packet).encode()
    packet_len = len(packet)
    s.send(packet_len.to_bytes(2) + packet)
    
def broadcast_packet(s, listener, packet):
    packet = json.dumps(packet).encode()
    packet_len = len(packet)
    
    for s in s.keys():
        if s is not listener:
            s.send(packet_len.to_bytes(2) + packet)