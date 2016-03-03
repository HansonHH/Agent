from request import *

# List servers
def nova_list_servers(env):
    
    # Retrive token from request
    X_AUTH_TOKEN = env['HTTP_X_AUTH_TOKEN']
    
    # Retrive tenant id by regular expression 
    tenant_id_pattern = re.compile(r'(?<=/v2.1/).*(?=/servers)')
    match = tenant_id_pattern.search(env['PATH_INFO'])
    TENANT_ID = match.group()
    
    # Create suffix of service url
    url_suffix = config.get('Nova', 'nova_public_interface') + '/v2.1/' + TENANT_ID + '/servers'
    
    # Get generated threads 
    threads = generate_threads(X_AUTH_TOKEN, url_suffix, GET_request_to_cloud)
    
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
	
    # Create suffix of service url
    url_suffix = config.get('Nova', 'nova_public_interface') + '/v2.1/' + TENANT_ID + '/servers/detail'
    
    # Get generated threads 
    threads = generate_threads(X_AUTH_TOKEN, url_suffix, GET_request_to_cloud)
    
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
	
    # Create suffix of service url
    url_suffix = config.get('Nova', 'nova_public_interface') + env['PATH_INFO'] 
    
    # Get generated threads 
    threads = generate_threads(X_AUTH_TOKEN, url_suffix, GET_request_to_cloud)
    
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
	        itemNotFound = parsed_json['itemNotFound']
                pass
            # VM found
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
	    return 'Failed to find server details'
	
    return response


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

