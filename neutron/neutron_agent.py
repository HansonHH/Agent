from nova.nova_agent import *

# List networks
def neutron_list_networks(env):
	
	# Retrive token from request
	X_AUTH_TOKEN = env['HTTP_X_AUTH_TOKEN']
	
	# Deliver request to clouds 
	# Create urls of clouds
	urls = []
	for site in SITES.values():
		url = site + ':' + config.get('Neutron','neutron_public_interface') + '/v2.0/networks'
		urls.append(url)
	headers ={'X-Auth-Token':X_AUTH_TOKEN}
        print urls
	# Create threads
	threads = [None] * len(urls)
	for i in range(len(threads)):
		threads[i] = ThreadWithReturnValue(target = GET_request_to_cloud, args=(urls[i], headers,))
	
	# Launch threads
	for i in range(len(threads)):
		threads[i].start()
	
	# Initiate response data structure
	json_data = {'networks':[]}	
        
	# Wait until threads terminate
	for i in range(len(threads)):
		
		# Parse response from site	
		parsed_json = json.loads(threads[i].join())
                
		# Get cloud site information by using regualr expression	
		site_pattern = re.compile(r'(?<=http://).*(?=:)')
		match = site_pattern.search(vars(threads[i])['_Thread__args'][0])
		# IP address of cloud
		site_ip = match.group()
		# Find name of cloud
		site = SITES.keys()[SITES.values().index('http://'+site_ip)]

		# If VM exists in cloud
		if len(parsed_json['networks']) != 0:
			# Recursively look up VMs
			for i in range(len(parsed_json['networks'])):
				parsed_json['networks'][i]['site_ip'] = site_ip
				parsed_json['networks'][i]['site'] = site
				
				#print site
				json_data['networks'].append(parsed_json['networks'][i])
	
	response = json.dumps(json_data)
	
	return response

# Show network details
def neutron_show_network_details(env):
	
	# Retrive token from request
	X_AUTH_TOKEN = env['HTTP_X_AUTH_TOKEN']
	
	# Deliver request to clouds 
	# Create urls of clouds
	urls = []
	for site in SITES.values():
		url = site + ':' + config.get('Neutron','neutron_public_interface') + env['PATH_INFO']
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
		try:
			parsed_json = json.loads(threads[i].join())
		   		
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
			return 'Failed to find network details'

