from nova.nova_agent import *
from request import *
from common import *
from db import *

AGENT_NEUTRON_ENGINE_CONNECTION = 'mysql+mysqldb://%s:%s@localhost/%s' % (DATABASE_USERNAME, DATABASE_PASSWORD, DATABASE_NAME)

# List networks
def neutron_list_networks(env):
	
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
    json_data = {'networks':[]}	
    headers = [('Content-Type','application/json')]	
    status_code = ''

    # Wait until threads terminate
    for i in range(len(threads)):
		
	# Parse response from site	
        try:

	    response = json.loads(threads[i].join()[0])
            status_code = str(threads[i].join()[1])

	    # If network exists in cloud
	    if len(response['networks']) != 0:

	        # Recursively look up networks
	        for j in range(len(response['networks'])):
                    # Add cloud info to response	
                    new_response = add_cloud_info_to_response(vars(threads[i])['_Thread__args'][0], response['networks'][j])
		    json_data['networks'].append(new_response)

        except:
            status_code = str(threads[i].join()[1])

    # Create status code response
    # If there exists at least one network
    if len(json_data['networks']) != 0:
        res = json.dumps(json_data)
    # No network exists
    elif len(json_data['networks']) == 0:
        res = json.dumps({'networks':[]})

    return (res, status_code, headers)


# Show network details
def neutron_show_network_details(env):
	
    # Retrive token from request
    X_AUTH_TOKEN = env['HTTP_X_AUTH_TOKEN']
	
    # Create suffix of service url
    url_suffix = config.get('Neutron', 'neutron_public_interface') + env['PATH_INFO']
    
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
            
            # If network not found
            try:
	        networkNotFound = response['NeutronError']
                res = json.dumps(response)
                status_code = str(threads[i].join()[1])
            # Network found
            except:
                normal_status_code = str(threads[i].join()[1])
	        # Add cloud info to response 
                response = add_cloud_info_to_response(vars(threads[i])['_Thread__args'][0], response)
                
                res = json.dumps(response)
    
                return (res, status_code, headers)
			
	except:
            status_code = str(threads[i].join()[1])
            res = threads[i].join()[0]

    return (res, status_code, headers)



# Create network                    
def neutron_create_network(env):
    
    # Retrive token from request
    X_AUTH_TOKEN = env['HTTP_X_AUTH_TOKEN']
    
    # Request data 
    PostData = env['wsgi.input'].read()
    
    # Construct url for creating network
    cloud_name = 'Cloud3'
    cloud_address = 'http://10.0.1.12'
    #url = cloud_address + ':' + config.get('Neutron','neutron_public_interface') + '/v2.0/networks' 
    url = cloud_address + ':' + config.get('Neutron','neutron_public_interface') + env['PATH_INFO'] 
    # Create header
    headers = {'Content-Type': 'application/json', 'X-Auth-Token': X_AUTH_TOKEN}
    
    response = POST_request_to_cloud(url, headers, PostData)
    
    # If network is successfully created in cloud
    if str(response.status_code) == '201':

        # Retrive information from response
        tenant_id = response.json()['network']['tenant_id'] 
        network_id = response.json()['network']['id'] 
        network_name = response.json()['network']['name']
        
        new_network = Network(tenant_id = tenant_id, uuid_agent = uuid.uuid4(), uuid_cloud = network_id, network_name = network_name, cloud_name = cloud_name, cloud_address = cloud_address)
        # Add data to DB
        add_to_DB(AGENT_NEUTRON_ENGINE_CONNECTION, new_network)

    return response


# Delete network
def neutron_delete_network(env):

    # Retrive token from request
    X_AUTH_TOKEN = env['HTTP_X_AUTH_TOKEN']
   
    site_pattern = re.compile(r'(?<=/networks/).*')
    match = site_pattern.search(env['PATH_INFO'])
    network_id = match.group()   
    
    # Create suffix of service url
    url_suffix = config.get('Neutron', 'neutron_public_interface') + '/v2.0/networks/'  
    
    res = query_from_DB(AGENT_NEUTRON_ENGINE_CONNECTION, Network, Network.uuid_agent, network_id)
    
    urls = []
    for network in res:
        urls.append(network.cloud_address + ':' + url_suffix + network.uuid_cloud)

    # Get generated threads 
    threads = generate_threads_multicast(X_AUTH_TOKEN, urls, DELETE_request_to_cloud)

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
        
        # If Network deleted successfully
	if threads_json[i]['status_code'] == 204:
	   
            # Retrive network uuuid at cloud side
            request_url = vars(threads[i])['_Thread__args'][0]
            match = site_pattern.search(request_url)
            uuid_cloud = match.group()   
            
            # Delete network information in agetn DB 
            delete_from_DB(AGENT_NEUTRON_ENGINE_CONNECTION, Network, Network.uuid_cloud, uuid_cloud)
            return threads_json[i]
		
    if len(threads_json) != 0:
	return threads_json[0] 
    else:
	return 'Failed to delete network! \r\n'
    

# List subnets
def neutron_list_subnets(env):
	
    # Retrive token from request
    X_AUTH_TOKEN = env['HTTP_X_AUTH_TOKEN']
    
    # Create suffix of service url
    #url_suffix = config.get('Neutron', 'neutron_public_interface') + '/v2.0/subnets'
    url_suffix = config.get('Neutron', 'neutron_public_interface') + env['PATH_INFO']
    
    # Get generated threads 
    threads = generate_threads(X_AUTH_TOKEN, url_suffix, GET_request_to_cloud)
    
    # Launch threads
    for i in range(len(threads)):
	threads[i].start()
	
    # Initiate response data structure
    json_data = {'subnets':[]}	
    headers = [('Content-Type','application/json')]	
    status_code = ''

    # Wait until threads terminate
    for i in range(len(threads)):
		
	# Parse response from site	
        try:

	    response = json.loads(threads[i].join()[0])
            status_code = str(threads[i].join()[1])

	    # If subnet exists in cloud
	    if len(response['subnets']) != 0:

	        # Recursively look up subnets
	        for j in range(len(response['subnets'])):
                    # Add cloud info to response	
                    new_response = add_cloud_info_to_response(vars(threads[i])['_Thread__args'][0], response['subnets'][j])
		    json_data['subnets'].append(new_response)
        except:
            status_code = str(threads[i].join()[1])

    # Create status code response
    # If there exists at least one subnet
    if len(json_data['subnets']) != 0:
        res = json.dumps(json_data)
    # No subnet exists
    elif len(json_data['subnets']) == 0:
        res = json.dumps({'subnets':[]})

    return (res, status_code, headers)


# Show subnet details
def neutron_show_subnet_details(env):
	
    # Retrive token from request
    X_AUTH_TOKEN = env['HTTP_X_AUTH_TOKEN']
    
    # Create suffix of service url
    url_suffix = config.get('Neutron', 'neutron_public_interface') + env['PATH_INFO']
    
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
            
            # If network not found
            try:
	        networkNotFound = response['NeutronError']
                res = json.dumps(response)
                status_code = str(threads[i].join()[1])
            # Network found
            except:
                normal_status_code = str(threads[i].join()[1])
	        # Add cloud info to response 
                response = add_cloud_info_to_response(vars(threads[i])['_Thread__args'][0], response)
                res = json.dumps(response)
    
                return (res, status_code, headers)
			
	except:
            status_code = str(threads[i].join()[1])
            res = threads[i].join()[0]

    return (res, status_code, headers)


# Create subnet                    
def neutron_create_subnet(env):
    
    # Retrive token from request
    X_AUTH_TOKEN = env['HTTP_X_AUTH_TOKEN']
    
    # Request data 
    PostData = env['wsgi.input'].read()
    
    # Construct url for creating subnet
    url = 'http://10.0.1.12:' + config.get('Neutron','neutron_public_interface') + '/v2.0/subnets' 
    
    # Create header
    headers = {'Content-Type': 'application/json', 'X-Auth-Token': X_AUTH_TOKEN}
    
    response = POST_request_to_cloud(url, headers, PostData)

    return response


# Delete subnet
def neutron_delete_subnet(env):

    # Retrive token from request
    X_AUTH_TOKEN = env['HTTP_X_AUTH_TOKEN']
    
    # Create suffix of service url
    url_suffix = config.get('Neutron', 'neutron_public_interface') + env['PATH_INFO']
    
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
        # Subnet deleted successfully
	if threads_json[i]['status_code'] == 204:
	    return threads_json[i]
		
    if len(threads_json) != 0:
	return threads_json[0] 
    else:
	return 'Failed to delete subnet! \r\n'




