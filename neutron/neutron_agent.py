from nova.nova_agent import *
from request import *
from common import *
from models import *
from db import *

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
    url = 'http://10.0.1.11:' + config.get('Neutron','neutron_public_interface') + '/v2.0/networks' 
    # Create header
    headers = {'Content-Type': 'application/json', 'X-Auth-Token': X_AUTH_TOKEN}
    
    response = POST_request_to_cloud(url, headers, PostData)
    
    return response


# Delete network
def neutron_delete_network(env):

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
        # Network deleted successfully
	if threads_json[i]['status_code'] == 204:
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
    url = 'http://10.0.1.11:' + config.get('Neutron','neutron_public_interface') + '/v2.0/subnets' 
    
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




