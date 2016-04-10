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
#import uuid
#import os
import time



def agent_upload_binary_image_data_to_selected_cloud(env):

    print '!'*60
    #print env
        
    # Retrive token from request
    X_AUTH_TOKEN = env['HTTP_X_AUTH_TOKEN']

    # Request data 
    post_data_json = json.loads(env['wsgi.input'].read())

    original_image_uuid_cloud = post_data_json['image']['original_image_uuid_cloud']
    created_image_uuid_cloud = post_data_json['image']['created_image_uuid_cloud']
    cloud_address = post_data_json['image']['cloud_address']

    print original_image_uuid_cloud
    print created_image_uuid_cloud
    print cloud_address

    print '!'*60
    
    # Create header
    headers = {'Content-Type': 'application/octet-stream', 'X-Auth-Token': X_AUTH_TOKEN}
        
    url_suffix = config.get('Glance', 'glance_public_interface') + '/v2/images/'  
    url = cloud_address + ':' + url_suffix + created_image_uuid_cloud + '/file'

    # Upload binary image data to selected cloud
    image_file_path = IMAGE_FILE_PATH + original_image_uuid_cloud 
    
    print url
    print image_file_path
    
    try:    
        res = PUT_request_to_cloud(url, headers, image_file_path)
    except Exception as e:
        print e

    print '?'*60
    print res.status_code
    print '?'*60
    if res.status_code == 204:
        print 'Image uploaded successfully !!!'
            
        ACTIVE = False
        headers = {'X-Auth-Token': X_AUTH_TOKEN}
        url = cloud_address + ':' + config.get('Glance', 'glance_public_interface') + '/v2/images/' + created_image_uuid_cloud  
        
        while not ACTIVE:
            print 'Check if image status is active'
            time.sleep(5)
            res = GET_request_to_cloud(url, headers)
            if res.json()['status'] == "active":
                ACTIVE = True
        
        status_code = '204'
    
    else:
        print 'Failed to upload binary image data !!!'
    
        status_code = '409'
        
    headers = ''

    return status_code, headers, json.dumps('')
    



'''
def upload_binary_image_data_to_selected_cloud(X_AUTH_TOKEN, temp_file_path, cloud_address, created_image_uuid_cloud):

    # Create header
    headers = {'Content-Type': 'application/octet-stream', 'X-Auth-Token': X_AUTH_TOKEN}
    url = cloud_address + ':' + config.get('Glance', 'glance_public_interface') + '/v2/images/' + created_image_uuid_cloud + '/file' 

    res = PUT_request_to_cloud(url, headers, temp_file_path)
    
    if res.status_code == 204:
        
        ACTIVE = False
        headers = {'X-Auth-Token': X_AUTH_TOKEN}
        url = cloud_address + ':' + config.get('Glance', 'glance_public_interface') + '/v2/images/' + created_image_uuid_cloud  
        
        while not ACTIVE:
            print 'Check if image status is active'
            time.sleep(5)
            res = GET_request_to_cloud(url, headers)
            if res.json()['status'] == "active":
                ACTIVE = True
        
        return True
    else:
        return False
'''

