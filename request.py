#! /usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright © 2016 Xin Han <hxinhan@gmail.com>
#

import ConfigParser
from nova.thread import ThreadWithReturnValue
import ast
import requests
import json
import re

#from cStringIO import StringIO
#import cStringIO


config = ConfigParser.ConfigParser()
config.read('agent.conf')
SITES = ast.literal_eval(config.get('Clouds','sites'))
print SITES

# POST request cloud
def POST_request_to_cloud(url, headers, PostData):
    
    res = requests.post(url, headers = headers, data = PostData)
    
    return res

# PUT request t cloud
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



