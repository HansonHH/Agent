from request import *
from common import *

# List servers
def nova_list_servers(env):
    
    # Retrive token from request
    X_AUTH_TOKEN = env['HTTP_X_AUTH_TOKEN']
    
    url_suffix = config.get('Nova', 'nova_public_interface') + env['PATH_INFO']
    
    '''
    # Retrive tenant id by regular expression 
    tenant_id_pattern = re.compile(r'(?<=/v2.1/).*(?=/servers)')
    match = tenant_id_pattern.search(env['PATH_INFO'])
    TENANT_ID = match.group()
    
    # Create suffix of service url
    url_suffix = config.get('Nova', 'nova_public_interface') + '/v2.1/' + TENANT_ID + '/servers'
    '''
    
    # Get generated threads 
    threads = generate_threads(X_AUTH_TOKEN, url_suffix, GET_request_to_cloud)
    
    # Launch threads
    for i in range(len(threads)):
	threads[i].start()

    # Initiate response data structure
    json_data = {'servers':[]}	
    headers = [('Content-Type','application/json')]	
    status_code = ''

    # Wait until threads terminate
    for i in range(len(threads)):
		
	# Parse response from site	
        try:

	    response = json.loads(threads[i].join()[0])
            status_code = str(threads[i].join()[1])

	    # If image exists in cloud
	    if len(response['servers']) != 0:

	        # Recursively look up images
	        for j in range(len(response['servers'])):
                    # Add cloud info to response	
                    new_response = add_cloud_info_to_response(vars(threads[i])['_Thread__args'][0], response['servers'][j])
		    json_data['servers'].append(new_response)
                    
        except:
            status_code = str(threads[i].join()[1])
    
    # Create status code response
    # If there exists at least one image
    if len(json_data['servers']) != 0:
        res = json.dumps(json_data)
    # No image exists
    elif len(json_data['servers']) == 0:
        res = json.dumps({'servers':[]})

    return (res, status_code, headers)



# List details for servers
def nova_list_details_servers(env):
	
    # Retrive token from request
    X_AUTH_TOKEN = env['HTTP_X_AUTH_TOKEN']
    
    url_suffix = config.get('Nova', 'nova_public_interface') + env['PATH_INFO']
    
    # Get generated threads 
    threads = generate_threads(X_AUTH_TOKEN, url_suffix, GET_request_to_cloud)
    
    # Launch threads
    for i in range(len(threads)):
	threads[i].start()
	
    # Initiate response data structure
    json_data = {'servers':[]}	
    headers = [('Content-Type','application/json')]	
    status_code = ''
	
    # Wait until threads terminate
    for i in range(len(threads)):
	
        # Parse response from site	
        try:
		
	    response = json.loads(threads[i].join()[0])
            status_code = str(threads[i].join()[1])
		
            # If VM exists in cloud
	    if len(response['servers']) != 0:
	        # Recursively look up VMs
	        for j in range(len(response['servers'])):
		    # Add cloud info to response	
                    new_response = add_cloud_info_to_response(vars(threads[i])['_Thread__args'][0], response['servers'][j])
		    json_data['servers'].append(new_response)
                    
        except:
            status_code = str(threads[i].join()[1])
		
    # Create status code response
    # If there exists at least one image
    if len(json_data['servers']) != 0:
        res = json.dumps(json_data)
    # No image exists
    elif len(json_data['servers']) == 0:
        res = json.dumps({'servers':[]})
    
    return (res, status_code, headers)
    

# Show server details
def nova_show_server_details(env):

    # Retrive token from request
    X_AUTH_TOKEN = env['HTTP_X_AUTH_TOKEN']
	
    # Create suffix of service url
    url_suffix = config.get('Nova', 'nova_public_interface') + env['PATH_INFO'] 
    
    # Get generated threads 
    threads = generate_threads(X_AUTH_TOKEN, url_suffix, GET_request_to_cloud)
    
    # Launch threads
    for i in range(len(threads)):
	threads[i].start()
    
    # Initiate response data structure
    response = None
    headers = [('Content-Type','application/json')]	
    status_code = ''

    # Wait until threads terminate
    for i in range(len(threads)):
        # Parse response from site	
	try:
	    response = json.loads(threads[i].join()[0])
            
            # If VM not found
            try:
	        itemNotFound = response['itemNotFound']
                res = json.dumps(response)
                status_code = str(threads[i].join()[1])
            # VM found
            except:
                
                status_code = str(threads[i].join()[1])
                # Add cloud info to response 
                response = add_cloud_info_to_response(vars(threads[i])['_Thread__args'][0], response)
                res = json.dumps(response)
    
                return (res, status_code, headers)
			
	except:
            status_code = str(threads[i].join()[1])
            res = json.dumps(threads[i].join()[0])
    
    return (res, status_code, headers)


# Create VM                    
def nova_create_server(env):
    
    # Retrive token from request
    X_AUTH_TOKEN = env['HTTP_X_AUTH_TOKEN']
    
    # Request data 
    PostData = env['wsgi.input'].read()
    
    # Construct url for creating network
    url = 'http://10.0.1.12:' + config.get('Nova','nova_public_interface') + env['PATH_INFO'] 
    # Create header
    headers = {'Content-Type': 'application/json', 'X-Auth-Token': X_AUTH_TOKEN}
    
    response = POST_request_to_cloud(url, headers, PostData)
    
    return response

# Delete image
def nova_delete_server(env):
	
    # Retrive token from request
    X_AUTH_TOKEN = env['HTTP_X_AUTH_TOKEN']
    
    # Create suffix of service url
    url_suffix = config.get('Nova', 'nova_public_interface') + env['PATH_INFO'] 
    
    # Get generated threads 
    threads = generate_threads(X_AUTH_TOKEN, url_suffix, DELETE_request_to_cloud)

    # Launch threads
    for i in range(len(threads)):
	threads[i].start()

    threads_json = []
    # Wait until threads terminate
    for i in range(len(threads)):
	
	# Parse response from site	
	parsed_json = json.loads(threads[i].join())
	threads_json.append(parsed_json)

    for i in range(len(threads_json)):
        # Server delete successfully
	if threads_json[i]['status_code'] == 204:
	    return threads_json[i]
		
    if len(threads_json) != 0:
	return threads_json[0] 
    else:
	return 'Failed to delete server! \r\n'

# List servers
def nova_list_flavors(env):
    
    # Retrive token from request
    X_AUTH_TOKEN = env['HTTP_X_AUTH_TOKEN']
    
    url_suffix = config.get('Nova', 'nova_public_interface') + env['PATH_INFO']
    
    
    # Get generated threads 
    threads = generate_threads(X_AUTH_TOKEN, url_suffix, GET_request_to_cloud)
    
    # Launch threads
    for i in range(len(threads)):
	threads[i].start()

    # Initiate response data structure
    json_data = {'flavors':[]}	
    headers = [('Content-Type','application/json')]	
    status_code = ''

    # Wait until threads terminate
    for i in range(len(threads)):
		
	# Parse response from site	
        try:

	    response = json.loads(threads[i].join()[0])
            status_code = str(threads[i].join()[1])

	    # If image exists in cloud
	    if len(response['flavors']) != 0:

	        # Recursively look up images
	        for j in range(len(response['flavors'])):
                    # Add cloud info to response	
                    new_response = add_cloud_info_to_response(vars(threads[i])['_Thread__args'][0], response['flavors'][j])
		    json_data['flavors'].append(new_response)
                    
        except:
            status_code = str(threads[i].join()[1])

    # Create status code response
    # If there exists at least one image
    if len(json_data['flavors']) != 0:
        res = json.dumps(json_data)
    # No image exists
    elif len(json_data['flavors']) == 0:
        res = json.dumps({'flavors':[]})

    return (res, status_code, headers)


# List details for flavors
def nova_list_details_flavors(env):
	
    print '!'*80
    # Retrive token from request
    X_AUTH_TOKEN = env['HTTP_X_AUTH_TOKEN']
    
    url_suffix = config.get('Nova', 'nova_public_interface') + env['PATH_INFO']
    
    # Get generated threads 
    threads = generate_threads(X_AUTH_TOKEN, url_suffix, GET_request_to_cloud)
    
    # Launch threads
    for i in range(len(threads)):
	threads[i].start()
	
    # Initiate response data structure
    json_data = {'flavors':[]}	
    headers = [('Content-Type','application/json')]	
    status_code = ''
	
    # Wait until threads terminate
    for i in range(len(threads)):
	
        # Parse response from site	
        try:
		
	    response = json.loads(threads[i].join()[0])
            status_code = str(threads[i].join()[1])
		
            # If VM exists in cloud
	    if len(response['flavors']) != 0:
	        # Recursively look up VMs
	        for j in range(len(response['flavors'])):
		    # Add cloud info to response	
                    new_response = add_cloud_info_to_response(vars(threads[i])['_Thread__args'][0], response['flavors'][j])
		    json_data['flavors'].append(new_response)
                    
        except:
            status_code = str(threads[i].join()[1])
		
    # Create status code response
    # If there exists at least one image
    if len(json_data['flavors']) != 0:
        res = json.dumps(json_data)
    # No image exists
    elif len(json_data['flavors']) == 0:
        res = json.dumps({'flavors':[]})
    
    return (res, status_code, headers)


# Show server details
def nova_show_flavor_details(env):

    # Retrive token from request
    X_AUTH_TOKEN = env['HTTP_X_AUTH_TOKEN']
	
    # Create suffix of service url
    url_suffix = config.get('Nova', 'nova_public_interface') + env['PATH_INFO'] 
    
    # Get generated threads 
    threads = generate_threads(X_AUTH_TOKEN, url_suffix, GET_request_to_cloud)
    
    # Launch threads
    for i in range(len(threads)):
	threads[i].start()
    
    # Initiate response data structure
    response = None
    headers = [('Content-Type','application/json')]	
    status_code = ''

    # Wait until threads terminate
    for i in range(len(threads)):
        # Parse response from site	
	try:
	    response = json.loads(threads[i].join()[0])
            
            # If flavor not found
            try:
	        itemNotFound = response['itemNotFound']
                res = json.dumps(response)
                status_code = str(threads[i].join()[1])
            # VM found
            except:
                
                status_code = str(threads[i].join()[1])
                # Add cloud info to response 
                response = add_cloud_info_to_response(vars(threads[i])['_Thread__args'][0], response)
                res = json.dumps(response)
    
                return (res, status_code, headers)
			
	except:
            status_code = str(threads[i].join()[1])
            res = json.dumps(threads[i].join()[0])
    
    return (res, status_code, headers)


# Create flavor                    
def nova_create_flavor(env):
    
    # Retrive token from request
    X_AUTH_TOKEN = env['HTTP_X_AUTH_TOKEN']
    
    # Request data 
    PostData = env['wsgi.input'].read()
    
    # Construct url for creating network
    url = 'http://10.0.1.12:' + config.get('Nova','nova_public_interface') + env['PATH_INFO'] 
    # Create header
    headers = {'Content-Type': 'application/json', 'X-Auth-Token': X_AUTH_TOKEN}
    
    response = POST_request_to_cloud(url, headers, PostData)
    
    return response


# Delete flavor
def nova_delete_flavor(env):
	
    # Retrive token from request
    X_AUTH_TOKEN = env['HTTP_X_AUTH_TOKEN']
    
    # Create suffix of service url
    url_suffix = config.get('Nova', 'nova_public_interface') + env['PATH_INFO'] 
    
    # Get generated threads 
    threads = generate_threads(X_AUTH_TOKEN, url_suffix, DELETE_request_to_cloud)

    # Launch threads
    for i in range(len(threads)):
	threads[i].start()

    threads_json = []
    # Wait until threads terminate
    for i in range(len(threads)):
	
	# Parse response from site	
	parsed_json = json.loads(threads[i].join())
	threads_json.append(parsed_json)

    for i in range(len(threads_json)):
        # Server delete successfully
	if threads_json[i]['status_code'] == 204:
	    return threads_json[i]
		
    if len(threads_json) != 0:
	return threads_json[0] 
    else:
	return 'Failed to delete flavor! \r\n'


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

