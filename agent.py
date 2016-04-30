#! /usr/bin/env python
# -*- coding: utf-8 -*-
# vim:fenc=utf-8
#
# Distributed under terms of the MIT license.

"""

agent.py
Proxy functions for communication between agents

"""

from request import *
from common import *
from db import *
from models import *
import time
from cyclon.peer import *


# Agent upload binary image data to selected cloud from temporary file
def agent_upload_binary_image_data_to_selected_cloud(env):

    # Retrive token from request
    X_AUTH_TOKEN = env['HTTP_X_AUTH_TOKEN']

    # Request data 
    post_data_json = json.loads(env['wsgi.input'].read())

    original_image_uuid_cloud = post_data_json['image']['original_image_uuid_cloud']
    created_image_uuid_cloud = post_data_json['image']['created_image_uuid_cloud']
    cloud_address = post_data_json['image']['cloud_address']
    
    # Create header
    headers = {'Content-Type': 'application/octet-stream', 'X-Auth-Token': X_AUTH_TOKEN}
        
    url_suffix = config.get('Glance', 'glance_public_interface') + '/v2/images/'  
    url = cloud_address + ':' + url_suffix + created_image_uuid_cloud + '/file'

    # Upload binary image data to selected cloud
    image_file_path = IMAGE_FILE_PATH + original_image_uuid_cloud 

    try:
        # Get generated thread 
        threads = generate_threads_multicast_with_data(X_AUTH_TOKEN, headers, [url], PUT_request_to_cloud, [image_file_path])

        # Launch thread
        threads[0].start()

        res = threads[0].join()
    # If image file does not exist
    except:
        
        print 'image file does not exist ' * 30
        status_code = '409'
        headers = ''
        response = ''
        headers = res.headers
        headers['Content-Length'] = str(len(json.dumps(response)))
        headers = ast.literal_eval(str(headers)).items()

        return status_code, headers, json.dumps(response)


    if res.status_code == 204:
        print 'Image uploaded successfully !!!'
            
        ACTIVE = False
        headers = {'X-Auth-Token': X_AUTH_TOKEN}
        url = cloud_address + ':' + config.get('Glance', 'glance_public_interface') + '/v2/images/' + created_image_uuid_cloud  
        
        while not ACTIVE:
            print 'Check if image status is active'
            time.sleep(5)

            threads = generate_threads_multicast(X_AUTH_TOKEN, headers, [url], GET_request_to_cloud)
            threads[0].start()
            res = threads[0].join()

            #res = GET_request_to_cloud(url, headers)
            if res.json()['status'] == "active":
                ACTIVE = True
        
        status_code = '204'
    
    else:
        print 'Failed to upload binary image data !!!'
        status_code = '409'

    headers = ''
    response = ''
    headers = res.headers
    headers['Content-Length'] = str(len(json.dumps(response)))
    headers = ast.literal_eval(str(headers)).items()

    return status_code, headers, json.dumps(response)


# Launch Peer thread in order to make peer run CYCLON Protocol periodically
def agent_launch_cyclon_peer_thread():

    peer = Peer(INTERVAL, [])
    peer.setDaemon(True)
    peer.start()

# Agent changes view of its knowledge of the whole network periodically based on CYCLON protocol
def agent_cyclon_view_exchange(env):

    print 'CYCLON View Exchange'

    neighbor = mc.get("neighbors")[0]
    
    status_code = '200'
    headers = [('Content-Type', 'application/json; charset=UTF-8')]
    response = neighbor.ip_address + ', ' + str(neighbor.age)

    return status_code, headers, json.dumps(response)

# Act as introducer and handle request of new peer join
def agent_cyclon_new_peer_join(env):
    
    print 'CYCLON New Peer Join'
    print '123 '*200
    # Get neighbor list from memory cache
    neighbors = mc.get("neighbors")
    # Get new peer's request
    PostData = env['wsgi.input'].read()
    post_data_json = json.loads(PostData)

    new_peer_ip_address = post_data_json['new_peer']['ip_address']

    status_code = ''
    response = None
    # SIZE CACHE is not filled up yet, add new peer's information to agent's (act as introducer) memory cache
    if len(neighbors) < FIXED_SIZE_CACHE and not is_in_neighbors(get_neighbors_ip_list(neighbors), new_peer_ip_address):
        print 'SIZE CACHE is not yet filled up, send peer join notification to neighbors...'
        # Introducer sends notification of peer joining to its neighbors, instead of initiating random walk
        send_peer_join_notification(neighbors, new_peer_ip_address)

        #response = generate_neighbors_response(neighbors)
        response = ''
        status_code = '201'
        new_peer = Neighbor(new_peer_ip_address, 0)
        neighbors.append(new_peer)
        # Update neighbors list
        mc.set("neighbors", neighbors, 0)
    
    # SIZE CACHE is already filled up, then initiate random walk
    else:
        print 'SIZE CACHE is already filled up, then initiate random walk...'
        status_code = '202'

    #headers = [('Content-Type', 'application/json; charset=UTF-8')]

    #return status_code, headers, json.dumps(response)
    status_code = '200'
    headers = [('Content-Type', 'application/json; charset=UTF-8')]
    response = ''

    return status_code, headers, json.dumps(response)


# Introducer sends notification of peer joining to neighbors
def send_peer_join_notification(neighbors, new_peer_ip_address):

    print 'SEND NOTIFICATION OF PEER JOIN'

    headers = {'Content-Type': 'application/json'}
    agent_ip = 'http://' + get_lan_ip() + ':' + config.get('Agent', 'listen_port')
    post_data = {"new_peer":new_peer_ip_address}
    data_set = []
    neighbors_list = []
    for neighbor in neighbors:
        if agent_ip != neighbor.ip_address:
            url = neighbor.ip_address + '/v1/agent/cyclon/handle_peer_join_notification'
            neighbors_list.append(url)
	    data_set.append(json.dumps(post_data))

    if len(neighbors_list) != 0:

	#threads = generate_threads_multicast_with_data("", headers, neighbors_list, POST_request_to_cloud, data_set)
	threads = generate_threads_multicast_with_data("", headers, neighbors_list, POST_request_connection_close, data_set)
    
        # Launch threads
        for i in range(len(threads)):
            threads[i].start()

        # Wait until threads terminate
        for i in range(len(threads)):
	    res = threads[i].join()


def POST_request_connection_close(url ,headers, PostData):
    s = requests.session()
    #s.keep_alive = False
    res = requests.post(url, headers = headers, data = PostData)
    res.connection.close()
    print 'Connection closed... ' * 30


'''
# Generate response contatining n neighbors' information, n is less or equal to SHUFFLE_LENGTH
def generate_neighbors_response(neighbors):
    neighbors_list = []
    # If length of neighbors list is less than SHUFFLE_LENGTH, then add all neighbors' infomation to response
    if len(neighbors) <= SHUFFLE_LENGTH:
        for neighbor in neighbors:
            neighbors_list.append({"ip_address":neighbor.ip_address})
    # Pick SHUFFLE_LENGTH neighbors at random and add selected neighbors' information to response 
    else:
        random_neighbors = pick_neighbors_at_random(neighbors, SHUFFLE_LENGTH)
        for neighbor in neighbors:
            neighbors_list.append({"ip_address":neighbor.ip_address})

    return {"neighbors":neighbors_list}
'''

# Randomly pick n neighbors
def pick_neighbors_at_random(neighbors, number):

    # Select a cloud at random
    random_neighbors = []
    for i in range(number):
        neighbor =  random.choice(neighbors)
        random_neighbors.append(neighbor)
    # Remove duplicated neighbor
    random_neighbors2 = []
    random_neighbors = neighbors
    for i in range(len(random_neighbors)):
        if random_neighbors[i] not in random_neighbors2:
            random_neighbors2.append(random_neighbors[i])

    return random_neighbors2
    
# Handles peer join notification sent from new peer's introducer
def agent_cyclon_handle_peer_join_notification(env):
    print 'Handle Peer Join Notification !!!!!!!'
    
    recevied_data = json.loads(env['wsgi.input'].read())

    neighbors = mc.get("neighbors")
    # Randomly pick up a neighbor as response
    random_neighbor = random.choice(neighbors)
    
    # Set new peer's age to 0 and add its information to memory cache 
    if len(neighbors) < FIXED_SIZE_CACHE:
    	new_neighbor = Neighbor(recevied_data['new_peer'], 0)
	neighbors.append(new_neighbor)
    	mc.set("neighbors", neighbors, 0)
    
    print '%'*60
    print 'Random Neighbor IP Address...'
    print random_neighbor.ip_address

    headers = {'Content-Type': 'application/json'}
    url = recevied_data['new_peer'] + '/v1/agent/cyclon/receive_from_introducer_neighbors'
    dic = {'neighbor':{'ip_address':random_neighbor.ip_address, 'age':random_neighbor.age}}
    res = POST_request_to_cloud(url, headers, json.dumps(dic))
    res.connection.close()

    print '%'*60

    status_code = '200'
    #status_code = str(res.status_code)
    headers = [('Content-Type', 'application/json; charset=UTF-8')]
    response = ''

    return status_code, headers, json.dumps(response)


# New peer receives response from its introducer's neighbors
def agent_cyclon_receive_from_introducer_neighbors(env):
    print 'Receive from Introducer Neighbors !!!!!!!'
    
    received_data = json.loads(env['wsgi.input'].read())
    res_neighbor_ip = received_data['neighbor']['ip_address']
    res_neighbor_age = received_data['neighbor']['age']
    
    neighbors = mc.get("neighbors")
    neighbors_ip_list = get_neighbors_ip_list(neighbors)
    if len(neighbors) < FIXED_SIZE_CACHE and not is_in_neighbors(neighbors_ip_list, res_neighbor_ip):
        new_neighbor = Neighbor(res_neighbor_ip, res_neighbor_age)
        neighbors.append(new_neighbor)
        mc.set("neighbors", neighbors, 0)
    
    status_code = '200'
    headers = [('Content-Type', 'application/json; charset=UTF-8')]
    response = ''

    return status_code, headers, json.dumps(response)


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



