from cyclon.peer import *


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
    neighbors2 = []
    for i in range(len(neighbors)):
        neighbors_ip_list = get_neighbors_ip_list(neighbors2)
        if neighbors[i].ip_address not in neighbors_ip_list:
            neighbors2.append(neighbors[i])
    return neighbors2

FIXED_SIZE_CACHE = 4

neighbors = []
neighbors.append(Neighbor('http://10.0.1.11', 0))
neighbors.append(Neighbor('http://10.0.1.12', 0))

response_neighbors = []
for neighbor in neighbors:
    response_neighbors.append(neighbor)
#response_neighbors = neighbors
#response_neighbors.append(Neighbor('http://10.0.1.11', 0))
#response_neighbors.append(Neighbor('http://10.0.1.12', 0))

filtered_received_neighbors = []
filtered_received_neighbors.append(Neighbor('http://10.0.1.13',0))
filtered_received_neighbors.append(Neighbor('http://10.0.1.14',0))
filtered_received_neighbors.append(Neighbor('http://10.0.1.15',0))
filtered_received_neighbors.append(Neighbor('http://10.0.1.15',0))
filtered_received_neighbors.append(Neighbor('http://10.0.1.16',0))

filtered_received_neighbors = remove_neighbors_with_same_ip(filtered_received_neighbors)




# Firstly, use empty cache slots (if any)
if len(neighbors) < FIXED_SIZE_CACHE:
    for i in range(FIXED_SIZE_CACHE-len(neighbors)):
        neighbors_ip_list = get_neighbors_ip_list(neighbors)
        random_neighbor = random.choice(filtered_received_neighbors)
        if not is_in_neighbors(neighbors_ip_list, random_neighbor.ip_address):
            neighbors.append(random_neighbor)
            filtered_received_neighbors = remove_from_list(filtered_received_neighbors, random_neighbor)

for neighbor in neighbors:
    print neighbor
print '-'*100
for neighbor in response_neighbors:
    print neighbor

print '!'*100
print '*'*50
print len(neighbors)
print len(response_neighbors)
print len(filtered_received_neighbors)
print '*'*50

# Secondly, replace entries among the ones originally sent to the other peer
if len(neighbors) == FIXED_SIZE_CACHE:
    response_neighbors_cp = response_neighbors
    for i in range(len(filtered_received_neighbors)):

        random_neighbor = random.choice(filtered_received_neighbors)
        filtered_received_neighbors = remove_from_list(filtered_received_neighbors, random_neighbor)

        random_response_neighbor = random.choice(response_neighbors_cp)
        response_neighbors_cp = remove_from_list(response_neighbors_cp, random_response_neighbor)

        neighbors = remove_from_list(neighbors, random_response_neighbor)
        neighbors.append(random_neighbor)


for neighbor in neighbors:
    print neighbor
print '-'*100
for neighbor in filtered_received_neighbors:
    print neighbor


