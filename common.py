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

config = ConfigParser.ConfigParser()
config.read('agent.conf')
SITES = ast.literal_eval(config.get('Clouds','sites'))

# A function to add cloud name and cloud ip to user response
def add_cloud_info_to_response(search_context, response):

    # Get cloud site information by using regualr expression	
    #site_pattern = re.compile(r'(?<=http://).*(?=:)')
    site_pattern = re.compile(r'(?<=http://).*')
    match = site_pattern.search(search_context)
    # IP address of cloud
    site_ip = match.group()
    # Find name of cloud
    site = SITES.keys()[SITES.values().index('http://'+site_ip)]
    
    # Add site information to json response
    response['site_ip'] = site_ip
    response['site'] = site	
    
    return response

# A function to send resonse to end-user if resource info dose exist in agent local DB
def non_exist_response(status_code, response_body):
    
    headers = {'Content-Type': 'application/json'} 
    headers = ast.literal_eval(str(headers)).items()
        
    return status_code, headers, json.dumps(response_body)
    


