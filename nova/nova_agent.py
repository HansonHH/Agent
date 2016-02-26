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
		threads[i] = ThreadWithReturnValue(target = GET_request_to_cloud, args=(urls[i], headers,))
	
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
				response = response + list_servers_response_message(server_name, server_id, site)
		# No server exist in site
		else:
			print 'NO SERVERS IN SITE!'
		
	return response


# List details for servers
def compute_list_details_servers(env):
	
	# Retrive token from request
	X_AUTH_TOKEN = env['HTTP_X_AUTH_TOKEN']
	# Retrive tenant id by regular expression 
	tenant_id_pattern = re.compile(r'(?<=/v2.1/).*(?=/servers)')
	match = tenant_id_pattern.search(env['PATH_INFO'])
	TENANT_ID = match.group()
	print TENANT_ID
	
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
				# Retrive host id
				host_id = parsed_json['servers'][i]['hostId']
				# Retrive creation time
				created = parsed_json['servers'][i]['created']
				# Retrive private address
				try:
					for j in range(len(parsed_json['servers'][i]['addresses']['private'])):
						if parsed_json['servers'][i]['addresses']['private'][j]['version'] == 4:
							private_address_ipv4 = parsed_json['servers'][i]['addresses']['private'][j]['addr'] + ', MAC:' + parsed_json['servers'][i]['addresses']['private'][j]['OS-EXT-IPS-MAC:mac_addr']
						elif parsed_json['servers'][i]['addresses']['private'][j]['version'] == 6:
							private_address_ipv6 = parsed_json['servers'][i]['addresses']['private'][j]['addr'] + ', MAC:' + parsed_json['servers'][i]['addresses']['private'][j]['OS-EXT-IPS-MAC:mac_addr']
				except:
					private_address_ipv4 = ''
					private_address_ipv6 = ''

				# Retrive AZ
				try:
					availability_zone = parsed_json['servers'][i]['OS-EXT-AZ:availability_zone']
				except:
					availability_zone = ''
				
				# Retrive image id
				try:
					image_id = parsed_json['servers'][i]['image']['id']
				except:
					image_id = ''
				# Retrive hypervisor
				try:
					hypervisor_hostname = parsed_json['servers'][i]['OS-EXT-SRV-ATTR:hypervisor_hostname']
				except:
					hypervisor_hostname = ''
				
				# Retrive task state
				try:
					task_state = parsed_json['servers'][i]['OS-EXT-STS:task_state']
				except:
					task_state = ''
				
				# Retrive vm state
				try:
					vm_state = parsed_json['servers'][i]['OS-EXT-STS:vm_state']
				except:
					vm_state = ''
				
				# Retrive status	
				try:
					status = parsed_json['servers'][i]['status']
				except:
					status = ''
				
				# Retrive host status	
				try:
					host_status = parsed_json['servers'][i]['host_status']
				except:
					host_status = ''
				
				# Retrive tenant id	
				tenant_id = parsed_json['servers'][i]['tenant_id']
				# Retrive user id	
				user_id = parsed_json['servers'][i]['user_id']
				
				# Retrive site url via regular expression
				cloud_pattern = re.compile(r'http://.*(?=:)')
				match = cloud_pattern.search(parsed_json['servers'][i]['links'][0]['href'])
				# Find site by url
				site = SITES.keys()[SITES.values().index(match.group())]
				# Create response message to client
				#response = response + list_details_response_message(server_name, server_id, site)
				response = response + list_details_response_message(server_name, server_id, host_id, created, private_address_ipv4, private_address_ipv6, availability_zone, image_id,hypervisor_hostname, task_state, vm_state, status, host_status, tenant_id, user_id, site)
		# No server exist in site
		else:
			print 'NO SERVERS IN SITE!'
		
	return response

# Send request to cloud
def GET_request_to_cloud(url, headers):
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
def list_servers_response_message(server_name, server_id, site):
	
	# Construct response to client 	
	response = '-'*60 + '\r\n' + 'server name: %s\r\n'% server_name
	response = response + 'server id: %s\r\n' % server_id
	response = response + 'site: %s\r\n' % site
	response = response + '-'*60 + '\r\n'
	
	return response 

# Response message to client
def list_details_response_message(server_name, server_id, host_id, created, private_address_ipv4, private_address_ipv6, availability_zone, image_id, hypervisor_hostname, task_state, vm_state, status, host_status, tenant_id, user_id, site):
#def list_details_servers_response_message(server_name, server_id, site):
	
	# Construct response to client 	
	response = '-'*60 + '\r\n' + 'server name: %s\r\n'% server_name
	response = response + 'server id: %s\r\n' % server_id
	response = response + 'host_id: %s\r\n' % host_id
	response = response + 'created: %s\r\n' % created
	response = response + 'private_address_ipv4: %s\r\n' % private_address_ipv4
	response = response + 'private_address_ipv6: %s\r\n' % private_address_ipv6
	response = response + 'availability_zone: %s\r\n' % availability_zone
	response = response + 'image_id: %s\r\n' % image_id
	response = response + 'hypervisor_hostname: %s\r\n' % hypervisor_hostname
	response = response + 'task_state: %s\r\n' % task_state
	response = response + 'vm_state: %s\r\n' % vm_state
	response = response + 'status: %s\r\n' % status
	response = response + 'host_status: %s\r\n' % host_status
	response = response + 'tenant_id: %s\r\n' % tenant_id
	response = response + 'user_id: %s\r\n' % user_id
	response = response + 'site: %s\r\n' % site
	response = response + '-'*60 + '\r\n'
	
	return response 
