import os
import re
import inspect
import json
import requests
import ConfigParser
import ast
from nova.thread import ThreadWithReturnValue

config = ConfigParser.ConfigParser()
config.read('agent.conf')
SITES = ast.literal_eval(config.get('Clouds','sites'))
print SITES

# Token authentication with scoped authorization
def compute_list_servers(env):

	# Retrive token from request
	X_AUTH_TOKEN = env['HTTP_X_AUTH_TOKEN']
	# Retrive tenant id by regular expression 
	tenant_id_pattern = re.compile(r'(?<=/v2.1/).*(?=/servers)')
	match = tenant_id_pattern.search(env['PATH_INFO'])
	TENANT_ID = match.group()
	
	# Deliver request to clouds 
	# Create urls of clouds
	urls = []
	for site in SITES.values():
		url = site + ':' + config.get('Nova','nova_public_interface') + '/v2.1/' + TENANT_ID + '/servers' 
		urls.append(url)
	headers ={'X-Auth-Token':X_AUTH_TOKEN}

	# Create threads
	threads = [None] * len(urls)
	for i in range(len(threads)):
		threads[i] = ThreadWithReturnValue(target = request_to_cloud, args=(urls[i], headers,))
	
	# Launch threads
	for i in range(len(threads)):
		threads[i].start()

	response = ''	
	# Wait until threads terminate
	for i in range(len(threads)):
		
		# Parse response from site	
		parsed_json = json.loads(threads[i].join())
		# Servers exist in site
		if len(parsed_json['servers']) != 0:

			for i in range(len(parsed_json['servers'])):
				# Retrive server name
				server_name = parsed_json['servers'][i]['name']
				# Retrive server id
				server_id = parsed_json['servers'][i]['id']
				# Retrive site url via regular expression
				cloud_pattern = re.compile(r'http://.*(?=:)')
				match = cloud_pattern.search(parsed_json['servers'][i]['links'][0]['href'])
				# Find site by url
				site = SITES.keys()[SITES.values().index(match.group())]
				# Create response message to client
				response = response + response_message(server_name, server_id, site)
		# No server exist in site
		else:
			print 'NO SERVERS IN CLOUD!'
		
	return response

# Send request to cloud
def request_to_cloud(url, headers):
	res = requests.get(url, headers = headers)
	return res.text

# Print out status code and response from Keystone
def show_response(functionname,response):
	print '-'*60
	print 'Function Name: %s' % functionname
	print 'Statu Code: %s' % response.status_code
	if response.status_code == 400:
		print 'Bad Request!'
	elif response.status_code == 401:
		print 'Unauthorized!'
	elif response.status_code == 403:
		print 'Forbidden!'
	elif response.status_code == 404:
		print 'Not Found!'
	elif response.status_code == 405:
		print 'Bad Method!!'
	print '-'*60

# Response message to client
def response_message(server_name, server_id, site):
	
	# Construct response to client 	
	response = '-'*60 + '\r\n' + 'server name: %s\r\n'% server_name
	response = response + 'server id: %s\r\n' % server_id
	response = response + 'site: %s\r\n' % site
	response = response + '-'*60 + '\r\n'
	
	return response 

