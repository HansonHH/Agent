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

	# If network exists in cloud
	if len(parsed_json['networks']) != 0:
	    # Recursively look up networks
	    for i in range(len(parsed_json['networks'])):
		parsed_json['networks'][i]['site_ip'] = site_ip
		parsed_json['networks'][i]['site'] = site
				
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
    
    headers = {'X-Auth-Token':X_AUTH_TOKEN}
	
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

# Create network                    
def neutron_create_network(env):
    print 'NEUTRON_CREATE_NETWORK'
    
    # Retrive token from request
    X_AUTH_TOKEN = env['HTTP_X_AUTH_TOKEN']
    
    
    return '123'

# List subnets
def neutron_list_subnets(env):
	
    # Retrive token from request
    X_AUTH_TOKEN = env['HTTP_X_AUTH_TOKEN']
	
    # Deliver request to clouds 
    # Create urls of clouds
    urls = []
    for site in SITES.values():
	url = site + ':' + config.get('Neutron','neutron_public_interface') + '/v2.0/subnets'
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
    json_data = {'subnets':[]}	
        
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

	# If subnet exists in cloud
	if len(parsed_json['subnets']) != 0:
	    # Recursively look up subnets
	    for i in range(len(parsed_json['subnets'])):
		parsed_json['subnets'][i]['site_ip'] = site_ip
		parsed_json['subnets'][i]['site'] = site
				
		json_data['subnets'].append(parsed_json['subnets'][i])
	
    response = json.dumps(json_data)
	
    return response

# Show subnet details
def neutron_show_subnet_details(env):
	
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
    response = ''	

    # Wait until threads terminate
    for i in range(len(threads)):
		
	# Parse response from site	
	try:
	    parsed_json = json.loads(threads[i].join())
            try:
                error = parsed_json['NeutronError']
                pass
            # No NeutronError return
            except:
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
	except:
	    return 'Failed to find subnet details'
	
    return response
