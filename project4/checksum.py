
def pack_ip(ip):
    return bytes(list(map(int, ip.split('.'))))


def get_addr_bytestrings(addrs_string):
    addrs = addrs_string.split()
    addr1 = pack_ip(addrs[0])
    addr2 = pack_ip(addrs[1])
    return addr1, addr2


for i in range(10):
    with open(f"tcp_data/tcp_addrs_{i}.txt", 'rb') as fp:
        addrs = fp.read()

