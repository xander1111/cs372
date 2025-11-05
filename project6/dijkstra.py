import sys
import json
import math  # If you want to use math.inf for infinity
from functools import reduce
import heapq


class Node:
    def __init__(self, name, dist=math.inf):
        self.name = name
        self.dist = dist
        self.prev = None
    
    def __gt__(self, other):
        return self.dist > other.dist
    
    def __lt__(self, other):
        return self.dist < other.dist
    
    def __eq__(self, other):
        return self.dist == other.dist


def ipv4_to_value(ipv4_addr):
    nums = [int(x) for x in ipv4_addr.split('.')]
    shifted_nums = [nums[len(nums) - 1 - i] << (i * 8) for i in range(len(nums))]
    return reduce(lambda x, y: x | y , shifted_nums, 0)


def get_subnet_mask_value(slash):
    subnet_len = int(slash.split("/")[1])
    return ((1 << subnet_len) - 1) << 32 - subnet_len


def ips_same_subnet(ip1, ip2, slash):
    addr1 = ipv4_to_value(ip1)
    addr2 = ipv4_to_value(ip2)
    mask = get_subnet_mask_value(slash)
    
    return addr1 & mask == addr2 & mask


def find_router_for_ip(routers, ip):
    for router_ip, router_details in routers.items():
        if ips_same_subnet(ip, router_ip, router_details["netmask"]):
            return router_ip


def get_path_to(graph, dest):
    path = []
    next = dest
    while next is not None:
        path.append(next)
        next = graph[next].prev
        
    path.reverse()
    return path


def dijkstras_shortest_path(routers, src_ip, dest_ip):
    """
    This function takes a dictionary representing the network, a source
    IP, and a destination IP, and returns a list with all the routers
    along the shortest path.

    The source and destination IPs are **not** included in this path.

    Note that the source IP and destination IP will probably not be
    routers! They will be on the same subnet as the router. You'll have
    to search the routers to find the one on the same subnet as the
    source IP. Same for the destination IP. [Hint: make use of your
    find_router_for_ip() function from the last project!]

    The dictionary keys are router IPs, and the values are dictionaries
    with a bunch of information, including the routers that are directly
    connected to the key.

    This partial example shows that router `10.31.98.1` is connected to
    three other routers: `10.34.166.1`, `10.34.194.1`, and `10.34.46.1`:

    {
        "10.34.98.1": {
            "connections": {
                "10.34.166.1": {
                    "netmask": "/24",
                    "interface": "en0",
                    "ad": 70
                },
                "10.34.194.1": {
                    "netmask": "/24",
                    "interface": "en1",
                    "ad": 93
                },
                "10.34.46.1": {
                    "netmask": "/24",
                    "interface": "en2",
                    "ad": 64
                }
            },
            "netmask": "/24",
            "if_count": 3,
            "if_prefix": "en"
        },
        ...

    The "ad" (Administrative Distance) field is the edge weight for that
    connection.

    **Strong recommendation**: make functions to do subtasks within this
    function. Having it all built as a single wall of code is a recipe
    for madness.
    """
    src_router = find_router_for_ip(routers, src_ip)
    dest_router = find_router_for_ip(routers, dest_ip)
    
    if src_router == dest_router:
        # If both IP's use the same router, they're on the same network and we don't have to do any routing
        return []  
    
    vertices = {router: Node(router) if router != src_router else Node(router, 0) for router in routers.keys()}
    
    queue = list(vertices.values())
    heapq.heapify(queue)
    
    while queue:
        current = heapq.heappop(queue)
        
        for neighbor_name, connection_info in routers[current.name]["connections"].items():
            dist = connection_info["ad"]
            if (dist + current.dist) < vertices[neighbor_name].dist:
                vertices[neighbor_name].dist = dist + current.dist
                vertices[neighbor_name].prev = current.name
                
                heapq.heappush(queue, vertices[neighbor_name])


    return get_path_to(vertices, dest_router)

#------------------------------
# DO NOT MODIFY BELOW THIS LINE
#------------------------------
def read_routers(file_name):
    with open(file_name) as fp:
        data = fp.read()

    return json.loads(data)

def find_routes(routers, src_dest_pairs):
    for src_ip, dest_ip in src_dest_pairs:
        path = dijkstras_shortest_path(routers, src_ip, dest_ip)
        print(f"{src_ip:>15s} -> {dest_ip:<15s}  {repr(path)}")

def usage():
    print("usage: dijkstra.py infile.json", file=sys.stderr)

def main(argv):
    try:
        router_file_name = argv[1]
    except:
        usage()
        return 1

    json_data = read_routers(router_file_name)

    routers = json_data["routers"]
    routes = json_data["src-dest"]

    find_routes(routers, routes)

if __name__ == "__main__":
    sys.exit(main(sys.argv))
    
