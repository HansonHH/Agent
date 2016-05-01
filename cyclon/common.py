import ConfigParser
import memcache
import socket
import os
import random


config = ConfigParser.ConfigParser()
config.read('agent.conf')

INTERVAL = int(config.get('CYCLON', 'interval'))
FIXED_SIZE_CACHE = int(config.get('CYCLON', 'fixed_size_cache'))
SHUFFLE_LENGTH = int(config.get('CYCLON', 'shuffle_length'))
RANDOM_WALK_TTL = int(config.get('CYCLON', 'random_walk_TTL'))
MEMCACHED_SERVER_IP = config.get('CYCLON', 'memcached_server_ip')

mc = memcache.Client([MEMCACHED_SERVER_IP], debug=1)

def get_interface_ip(ifname):
    import fcntl
    import struct
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    return socket.inet_ntoa(fcntl.ioctl(s.fileno(), 0x8915, struct.pack('256s', ifname[:15]))[20:24])

# Get agent's lan ip address
def get_lan_ip():
    ip = socket.gethostbyname(socket.gethostname())
    if ip.startswith("127.") and os.name != "nt":
        interfaces = ["eth1", "eth0", "eth2","wlan0","wlan1","wifi0","ath0","ath1","ppp0"]
        for ifname in interfaces:
            try:
                ip = get_interface_ip(ifname)
                break
            except IOError:
                pass
    return ip

# Remove a item from a list
def remove_from_list(items, target):
    new_items = []
    for item in items:
        if item != target:
            new_items.append(item)
    return new_items

# Return a list of neighbors' ip addresses
def get_neighbors_ip_list(neighbors):
    neighbors_ip_list = []
    for neighbor in neighbors:
        neighbors_ip_list.append(neighbor.ip_address)
    return neighbors_ip_list

# Check if new peer is already in
def is_in_neighbors(neighbors_ip_list, new_peer_ip_address):
    if new_peer_ip_address in neighbors_ip_list:
        return True
    else:
        return False

# Remove duplicated neighbor
def remove_neighbors_with_same_ip(neighbors):

    new_neighbors = []
    for i in range(len(neighbors)):
        neighbors_ip_list = get_neighbors_ip_list(new_neighbors)
        if neighbors[i].ip_address not in neighbors_ip_list:
            new_neighbors.append(neighbors[i])
    return new_neighbors

# Randomly pick n neighbors
def pick_neighbors_at_random(neighbors, number):

    # Select a cloud at random
    random_neighbors = []
    for i in range(number):
        neighbor =  random.choice(neighbors)
        random_neighbors.append(neighbor)

    return random_neighbors


def update_neighbors_cache(neighbors, received_neighbors, response_neighbors):

    # Discard entries pointing to agent, and entries that are already in anget's cache
    filtered_received_neighbors = []
    neighbors_ip_list = get_neighbors_ip_list(neighbors)
    print neighbors_ip_list
    for neighbor in received_neighbors:
        print neighbor
        #if neighbor['ip_address'] not in neighbors_ip_list and neighbor['ip_address'] != AGENT_IP:
        if neighbor['ip_address'] != AGENT_IP:
            neighbor = Neighbor(neighbor['ip_address'], neighbor['age'])
            filtered_received_neighbors.append(neighbor)
    
    # Remove redundant neighbors	
    filtered_received_neighbors = remove_neighbors_with_same_ip(filtered_received_neighbors)

    # Update peer's cache to include all remaining entries 
    # Firstly, use empty cache slots (if any)
    if len(neighbors) < FIXED_SIZE_CACHE:
        for i in range(FIXED_SIZE_CACHE-len(neighbors)):
            neighbors_ip_list = get_neighbors_ip_list(neighbors)
            random_neighbor = random.choice(filtered_received_neighbors)
            #if not is_in_neighbors(neighbors_ip_list, random_neighbor.ip_address):
            #    neighbors.append(random_neighbor)
            #    filtered_received_neighbors = remove_from_list(filtered_received_neighbors, random_neighbor)
            neighbors.append(random_neighbor)
            filtered_received_neighbors = remove_from_list(filtered_received_neighbors, random_neighbor)

    # Secondly, replace entries among the ones originally sent to the other peer
    if len(neighbors) == FIXED_SIZE_CACHE:
        #response_neighbors_cp = response_neighbors
        for i in range(len(filtered_received_neighbors)):

            random_neighbor = random.choice(filtered_received_neighbors)
            filtered_received_neighbors = remove_from_list(filtered_received_neighbors, random_neighbor)

            random_response_neighbor = random.choice(response_neighbors)
            response_neighbors = remove_from_list(response_neighbors, random_response_neighbor)

            neighbors = remove_from_list(neighbors, random_response_neighbor)
            neighbors.append(random_neighbor)

    mc.set("neighbors", neighbors, 0)





