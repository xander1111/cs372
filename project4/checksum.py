
def pack_ip(ip):
    return bytes(list(map(int, ip.split('.'))))


def get_addr_bytestrings(addrs_string):
    addrs = addrs_string.split()
    addr1 = pack_ip(addrs[0])
    addr2 = pack_ip(addrs[1])
    return addr1, addr2


def get_ip_pseudo_header(source_addr, dest_addr, data_len):
    data_len_bytes = data_len.to_bytes()
    data_len_padded = b'\x00' + data_len_bytes if len(data_len_bytes) < 2 else data_len_bytes
    return source_addr + dest_addr + b'\x00' + b'\x06' + data_len_padded


def checksum(packet):
    if len(packet) % 2 == 1:
        packet += b'\x00'
        
    offset = 0
    total = 0
    while offset < len(packet):
        word = int.from_bytes(packet[offset:offset + 2], "big")
        total += word
        total = (total & 0xffff) + (total >> 16)
        
        offset += 2
        
    return (~total) & 0xffff


for i in range(10):
    with open(f"tcp_data/tcp_addrs_{i}.txt", 'r') as addrs_fp:
        addrs_string = addrs_fp.read()
        with open(f"tcp_data/tcp_data_{i}.dat", 'rb') as data_fp:
            data = data_fp.read()
            
            source_addr, dest_addr = get_addr_bytestrings(addrs_string)
            ip_header = get_ip_pseudo_header(source_addr, dest_addr, len(data))
            
            tcp_data_checksum = int.from_bytes(data[16:18])
            data_zero_checksum = data[:16] + b'\x00\x00' + data[18:]
            
            calculated_checksum = checksum(ip_header + data_zero_checksum)           
            
            print("PASS" if calculated_checksum == tcp_data_checksum else "FAIL") 
            
