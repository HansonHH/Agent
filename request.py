#! /usr/bin/env python
# -*- coding: utf-8 -*-
#

import ConfigParser
from nova.thread import ThreadWithReturnValue
import ast
import requests
import json
import re

config = ConfigParser.ConfigParser()
config.read('agent.conf')
SITES = ast.literal_eval(config.get('Clouds','sites'))
print SITES

# POST request cloud
def POST_request_to_cloud(url, headers, PostData):
    
    res = requests.post(url, headers = headers, data = PostData)
    
    return res

# POST request cloud
def POST_request_to_peer(url, headers, timeout, PostData):
    
    res = requests.post(url, headers = headers, timeout = timeout, data = PostData)
    
    return res

# Close connection immediately after sending POST request
def POST_request_connection_close(url ,headers, PostData):
    
    res = requests.post(url, headers = headers, data = PostData)
    res.connection.close()

# PUT request to cloud
def PUT_request_to_cloud(url, headers, temp_file_path):

    f = open(temp_file_path, 'rb')
    res = requests.put(url, headers = headers, data = f)
    f.close()
    
    return res

# GET request to cloud
def GET_request_to_cloud(url, headers):
    
    res = requests.get(url, headers = headers)
    
    return res

# DELETE request to cloud
def DELETE_request_to_cloud(url, headers):
    
    res = requests.delete(url, headers = headers)
    
    return res

# A function to generate threads for boardcasting user request to clouds
def generate_threads(X_AUTH_TOKEN, url_suffix, target, headers):

    # Create urls of clouds
    urls = []
    for site in SITES.values():
        url = site + ':' + url_suffix
        urls.append(url)

    # Create threads
    threads = [None] * len(urls)
    for i in range(len(threads)):
            threads[i] = ThreadWithReturnValue(target = target, args = (urls[i], headers,))
    
    return threads

# A function to generate threads for multicasting user request to clouds
def generate_threads_multicast(X_AUTH_TOKEN, headers, urls, target):

    # Create threads
    threads = [None] * len(urls)
    for i in range(len(threads)):
            threads[i] = ThreadWithReturnValue(target = target, args = (urls[i], headers,))
    
    return threads


# A function to generate threads for multicasting user request to clouds
def generate_threads_multicast_with_data(X_AUTH_TOKEN, headers, urls, target, data_set):

    # Create threads
    threads = [None] * len(urls)
    for i in range(len(threads)):
        threads[i] = ThreadWithReturnValue(target = target, args = (urls[i], headers, data_set[i],))
    
    return threads



