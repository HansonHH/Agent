#! /usr/bin/env python
# -*- coding: utf-8 -*-
# vim:fenc=utf-8
#

"""

Common functions

"""
import ConfigParser
import ast
import re
import json
import random
import os
import socket

config = ConfigParser.ConfigParser()
config.read('agent.conf')
SITES = ast.literal_eval(config.get('Clouds','sites'))

DATABASE_NAME = config.get('Database', 'DATABASE_NAME')
DATABASE_USERNAME = config.get('Database', 'DATABASE_USERNAME')
DATABASE_PASSWORD = config.get('Database', 'DATABASE_PASSWORD')
AGENT_DB_ENGINE_CONNECTION = 'mysql+mysqldb://%s:%s@localhost/%s' % (DATABASE_USERNAME, DATABASE_PASSWORD, DATABASE_NAME)

TEMP_IMAGE_PATH = config.get('Glance', 'temp_image_path')
IMAGE_FILE_PATH = config.get('Glance', 'image_file_path')

config = ConfigParser.ConfigParser()
config.read('agent.conf')

global NEIGHBORS
NEIGHBORS = []
INTERVAL = int(config.get('CYCLON', 'interval'))
FIXED_SIZE_CACHE = int(config.get('CYCLON', 'fixed_size_cache'))
SHUFFLE_LENGTH = int(config.get('CYCLON', 'shuffle_length'))


# A function to send resonse to end-user if resource info dose exist in agent local DB
def non_exist_response(status_code, response_body):
    
    headers = {'Content-Type': 'application/json'} 
    headers = ast.literal_eval(str(headers)).items()

    if type(response_body) == str:
        return status_code, headers, response_body
    elif type(response_body) == dict:
        return status_code, headers, json.dumps(response_body)

# A function to add cloud name and cloud ip to user response
def add_cloud_info_to_response(search_context, response):

    # Get cloud site information by using regualr expression	
    site_pattern = re.compile(r'(?<=http://).*')
    match = site_pattern.search(search_context)
    # IP address of cloud
    site_ip = match.group()
    # Find name of cloud
    site = SITES.keys()[SITES.values().index('http://'+site_ip)]

    # Add site information to json response
    try:
        response['site'] = response['site'] + ', ' + site + '-' + site_ip
    except:
        response['site'] = site + '-' + site_ip	

    return response

# Remove duplication information of response
def remove_duplicate_info(items, keyword):

    ids = []
    rs = []
    for item in items:
        if item not in rs and item[keyword] not in ids:
            ids.append(item[keyword])
            rs.append(item)
        else:
            for item2 in rs:
                if item[keyword] == item2[keyword]:
                    item2['site'] = item2['site'] + ', ' + item['site']
    return rs


# Modify response header in terms of Content-Length
def modify_response_header(headers, response_body):
    headers_dict = dict(headers)
    headers_dict['Content-Length'] = str(len(json.dumps(response_body)))
    headers = ast.literal_eval(str(headers_dict)).items()

    return headers

# A function to generate well-formatted response to end user
def generate_formatted_response(res, response_body):
    
    status_code = str(res.status_code)
    headers = res.headers
    headers['Content-Length'] = str(len(json.dumps(response_body)))
    headers = ast.literal_eval(str(headers)).items()

    return status_code, headers, json.dumps(response_body)

# Read image binary data by chunks
def readInChunks(fileObj, chunkSize = 4096):
    while True:
        data = fileObj.read(chunkSize)
        if not data:
            break
        yield data


def delete_temp_image_file(temp_file_path):
    # Delete temporary image file
    try:
        os.remove(temp_file_path)
    except:
        pass

def select_site_to_create_object():
    # Select a cloud at random
    #cloud_name =  random.choice(SITES.keys())
    #cloud_address = SITES[cloud_name]

    cloud_name = 'Cloud10'
    cloud_address = 'http://10.0.1.20'

    return cloud_name, cloud_address


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





