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
    print neighbor.ip_address
    print neighbor.age
    
    status_code = '200'
    headers = [('Content-Type', 'application/json; charset=UTF-8')]
    response = neighbor.ip_address + ', ' + str(neighbor.age)

    return status_code, headers, json.dumps(response)


def agent_cyclon_new_peer_join(env):
    
    print 'CYCLON View Exchange'
    # Get neighbor list from memory cache
    neighbors = mc.get("neighbors")
    # Get new peer's request
    PostData = env['wsgi.input'].read()
    post_data_json = json.loads(PostData)

    print '!'*60
    print post_data_json
    new_peer_ip_address = post_data_json['new_peer']['ip_address']
    print new_peer_ip_address
    for neighbor in neighbors:
        print "ip: %s, age: %s" % (neighbor.ip_address,neighbor.age)
    print '!'*60

    if len(neighbors) < FIXED_SIZE_CACHE:
        print 'len(neighbors) < FIXED_SIZE_CACHE !!!'
        new_peer = Neighbor(new_peer_ip_address, 0)
        response_list = neighbors
        neighbors.append(new_peer)
        # Update neighbors list
        mc.set("neighbors", neighbors)
        print len(neighbors)



