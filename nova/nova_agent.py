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

# List servers
def nova_list_servers(env):

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
		threads[i] = ThreadWithReturnValue(target = GET_request_to_cloud, args=(urls[i], headers,))
	
	# Launch threads
	for i in range(len(threads)):
		threads[i].start()
	
	# Initiate response data structure
	json_data = {'servers':[]}	

	# Wait until threads terminate
	for i in range(len(threads)):
		
		# Parse response from site	
		parsed_json = json.loads(threads[i].join())
		
		# If VM exists in cloud
		if len(parsed_json['servers']) != 0:
			# Recursively look up VMs
			for i in range(len(parsed_json['servers'])):
			
				# Get cloud site information by using regualr expression	
				site_pattern = re.compile(r'(?<=http://).*(?=:)')
				match = site_pattern.search(vars(threads[i])['_Thread__args'][0])
				# IP address of cloud
				site_ip = match.group()
				# Find name of cloud
				site = SITES.keys()[SITES.values().index('http://'+site_ip)]
				# Add site information to json response
				parsed_json['servers'][i]['site_ip'] = site_ip
				parsed_json['servers'][i]['site'] = site
		
				json_data['servers'].append(parsed_json['servers'][i])
	
	response = json.dumps(json_data)
	
	return response


# List details for servers
def nova_list_details_servers(env):
	
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
		url = site + ':' + config.get('Nova','nova_public_interface') + '/v2.1/' + TENANT_ID + '/servers/detail' 
		urls.append(url)
	headers ={'X-Auth-Token':X_AUTH_TOKEN}

	# Create threads
	threads = [None] * len(urls)
	for i in range(len(threads)):
		threads[i] = ThreadWithReturnValue(target = GET_request_to_cloud, args=(urls[i], headers,))
	
	# Launch threads
	for i in range(len(threads)):
		threads[i].start()
	
	# Initiate response data structure
	json_data = {'servers':[]}	
	
	# Wait until threads terminate
	for i in range(len(threads)):
		
		# Parse response from site	
		parsed_json = json.loads(threads[i].join())
		
		# If VM exists in cloud
		if len(parsed_json['servers']) != 0:
			# Recursively look up VMs
			for i in range(len(parsed_json['servers'])):
				
				# Get cloud site information by using regualr expression	
				site_pattern = re.compile(r'(?<=http://).*(?=:)')
				match = site_pattern.search(vars(threads[i])['_Thread__args'][0])
				# IP address of cloud
				site_ip = match.group()
				# Find name of cloud
				site = SITES.keys()[SITES.values().index('http://'+site_ip)]
				# Add site information to json response
				parsed_json['servers'][i]['site_ip'] = site_ip
				parsed_json['servers'][i]['site'] = site
				
				json_data['servers'].append(parsed_json['servers'][i])
		
	response = json.dumps(json_data)
		
	return response


# Show server details
def nova_show_server_details(env):

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
		url = site + ':' + config.get('Nova','nova_public_interface') + env['PATH_INFO'] 
		urls.append(url)
	headers ={'X-Auth-Token':X_AUTH_TOKEN}

	# Create threads
	threads = [None] * len(urls)
	for i in range(len(threads)):
		threads[i] = ThreadWithReturnValue(target = GET_request_to_cloud, args=(urls[i], headers,))
	
	# Launch threads
	for i in range(len(threads)):
		threads[i].start()
	
	# Initiate response data structure
	json_data = {}	
	
	# Wait until threads terminate
	for i in range(len(threads)):
		
		# Parse response from site	
		parsed_json = json.loads(threads[i].join())
		try:
				
			# Get cloud site information by using regualr expression	
			site_pattern = re.compile(r'(?<=http://).*(?=:)')
			match = site_pattern.search(vars(threads[i])['_Thread__args'][0])
			# IP address of cloud
			site_ip = match.group()
			# Find name of cloud
			site = SITES.keys()[SITES.values().index('http://'+site_ip)]
			# Add site information to json response
			parsed_json['site_ip'] = site_ip
			parsed_json['site'] = site
		
			response = json.dumps(parsed_json)

			return response
			
		except:
			pass	

	return 'Failed to find the VM\r\n'

# GET request to cloud
def GET_request_to_cloud(url, headers):
	res = requests.get(url, headers = headers)
	return res.text

# DELETE request to cloud
def DELETE_request_to_cloud(url, headers):
	res = requests.delete(url, headers = headers)
	dic = {'status_code':res.status_code, 'headers':str(res.headers), 'text':res.text}
	json_data = json.dumps(dic)
	return json_data

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

