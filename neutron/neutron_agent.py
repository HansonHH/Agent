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
    #cloud_name = 'Cloud1'
    #cloud_address = 'http://10.0.1.10'
    cloud_name = 'Cloud3'
    cloud_address = 'http://10.0.1.12'
    url = cloud_address + ':' + config.get('Neutron','neutron_public_interface') + env['PATH_INFO'] 
    # Create header
    headers = {'Content-Type': 'application/json', 'X-Auth-Token': X_AUTH_TOKEN}
    
    response = POST_request_to_cloud(url, headers, PostData)
    
    # If network is successfully created in cloud
    if str(response.status_code) == '201':

        # Retrive information from response
        response_json = response.json()
        tenant_id = response_json['network']['tenant_id'] 
        network_id = response_json['network']['id'] 
        network_name = response_json['network']['name']
        uuid_agent = str(uuid.uuid4())
        #uuid_agent = '038de0eb-c088-4817-95d3-581f8b1f97e0'
        
        new_network = Network(tenant_id = tenant_id, uuid_agent = uuid_agent, uuid_cloud = network_id, network_name = network_name, cloud_name = cloud_name, cloud_address = cloud_address)
        
        # Add data to DB
        add_to_DB(AGENT_NEUTRON_ENGINE_CONNECTION, new_network)

        status_code = str(response.status_code)
        headers = ast.literal_eval(str(response.headers)).items()
        response_json['network']['id'] =  uuid_agent

        return status_code, headers, json.dumps(response_json)
    
    else:
        status_code = str(response.status_code)
        headers = ast.literal_eval(str(response.headers)).items()

        return status_code, headers, json.dumps(response.json())


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
    
    # If network does not exist
    if res.count() == 0:
    
        response_message = "Network %s could not be found" % network_id
        response = {"NeutronError":{"detail":"","message":response_message,"type":"NetworkNotFound"}}
        status_code = '404'
        headers = {'Content-Type': 'application/json'} 
        headers = ast.literal_eval(str(headers)).items()
    
        return status_code, headers, json.dumps(response)
    
    # If network exists then delete
    else:

        urls = []
        for network in res:
            urls.append(network.cloud_address + ':' + url_suffix + network.uuid_cloud)

        # Get generated threads 
        threads = generate_threads_multicast(X_AUTH_TOKEN, urls, DELETE_request_to_cloud)

        # Launch threads
        for i in range(len(threads)):
	    threads[i].start()

        threads_res = []
    
        # Wait until threads terminate
        for i in range(len(threads)):
	
	    # Parse response from site	
	    res = threads[i].join()
	    threads_res.append(res)
    
        SUCCESS_threads = []
        FAIL_threads = []

        for i in range(len(threads_res)):
            print threads_res[i].status_code
        
            # If Network deleted successfully
	    if threads_res[i].status_code == 204:
	   
                # Retrive network uuid_cloud 
                request_url = vars(threads[i])['_Thread__args'][0]
                match = site_pattern.search(request_url)
                uuid_cloud = match.group()   
            
                # Delete subnet information in agent DB 
                delete_from_DB(AGENT_NEUTRON_ENGINE_CONNECTION, Subnet, Subnet.network_uuid_cloud, uuid_cloud)
                # Delete network information in agent DB 
                delete_from_DB(AGENT_NEUTRON_ENGINE_CONNECTION, Network, Network.uuid_cloud, uuid_cloud)
                SUCCESS_threads.append(threads_res[i])
            else:
                FAIL_threads.append(threads_res[i])

        if len(SUCCESS_threads) != 0:
            response = SUCCESS_threads[0]
            status_code = str(response.status_code)
            headers = ast.literal_eval(str(response.headers)).items()

            return status_code, headers, json.dumps(response.text)
        else:
            response = FAIL_threads[0]
            status_code = str(response.status_code)
            headers = ast.literal_eval(str(response.headers)).items()

            return status_code, headers, json.dumps(response.text)


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
    
    network_id = json.loads(PostData)['subnet']['network_id']
    network_uuid_agent = network_id
    
    # Query from local DB
    res = query_from_DB(AGENT_NEUTRON_ENGINE_CONNECTION, Network, Network.uuid_agent, network_id)
    
    # If network does not exist
    if res.count() == 0:
    
        response_message = "Network %s could not be found" % json.loads(PostData)['subnet']['network_id']
        response = {"NeutronError":{"detail":"","message":response_message,"type":"NetworkNotFound"}}
        status_code = '404'
        headers = {'Content-Type': 'application/json'} 
        headers = ast.literal_eval(str(headers)).items()
    
        return status_code, headers, json.dumps(response)

    # If network exists
    else:
    
        # Create suffix of service url
        url_suffix = config.get('Neutron', 'neutron_public_interface') + '/v2.0/subnets'  
        urls = []
        data_set = []
        for network in res:
            urls.append(network.cloud_address + ':' + url_suffix)
            post_data = PostData
            post_data_json = json.loads(post_data)
            post_data_json['subnet']['network_id'] = network.uuid_cloud
            data_set.append(json.dumps(post_data_json))

        # Get generated threads 
        threads = generate_threads_multicast_POST(X_AUTH_TOKEN, urls, POST_request_to_cloud, data_set)

        # Launch threads
        for i in range(len(threads)):
	    threads[i].start()

        threads_res = []
    
        # Wait until threads terminate
        for i in range(len(threads)):
	
	    # Parse response from site	
	    res = threads[i].join()
	    threads_res.append(res)

        SUCCESS_threads = []
        FAIL_threads = []
        uuid_agent = uuid.uuid4()
        
        # Retrive information from threads
        for i in range(len(threads_res)):
        
            # If Subnet created successfully
	    if threads_res[i].status_code == 201:
	    
                # Retrive network uuuid at cloud side
                request_url = vars(threads[i])['_Thread__args'][0]
                
                # Retrive information from response
                response_json = threads_res[i].json()
                tenant_id = response_json['subnet']['tenant_id'] 
                subnet_id = response_json['subnet']['id'] 
                subnet_name = response_json['subnet']['name']
                network_id = response_json['subnet']['network_id']
                # Retrive cloud name and cloud address
                site_pattern1 = re.compile(r'.*(?=/v2.0/)')
                match1 = site_pattern1.search(request_url)
                cloud_address_with_port = match1.group()   
                site_pattern2 = re.compile(r'.*(?=:)')
                match2 = site_pattern2.search(cloud_address_with_port)
                cloud_address = match2.group()   
                cloud_name = SITES.keys()[SITES.values().index(cloud_address)]
                
                new_subnet = Subnet(tenant_id = tenant_id, uuid_agent = uuid_agent, uuid_cloud = subnet_id, subnet_name = subnet_name, cloud_name = cloud_name, cloud_address = cloud_address, network_uuid_cloud = network_id)
                
                # Add data to DB
                add_to_DB(AGENT_NEUTRON_ENGINE_CONNECTION, new_subnet)
                
                SUCCESS_threads.append(threads_res[i])

            # If subnet failed to be created
            else:
                FAIL_threads.append(threads_res[i])

        if len(SUCCESS_threads) != 0:
        
            status_code = str(SUCCESS_threads[0].status_code)
            headers = ast.literal_eval(str(SUCCESS_threads[0].headers)).items()
            response_json = SUCCESS_threads[0].json()
            response_json['subnet']['id'] = query_from_DB(AGENT_NEUTRON_ENGINE_CONNECTION, Subnet, Subnet.uuid_cloud, response_json['subnet']['id'])[0].uuid_agent
            response_json['subnet']['network_id'] =  network_uuid_agent

            return status_code, headers, json.dumps(response_json)

        elif len(FAIL_threads) != 0:
            status_code = str(FAIL_threads[0].status_code)
            headers = ast.literal_eval(str(FAIL_threads[0].headers)).items()
            response_json = FAIL_threads[0].json()
            
            return status_code, headers, json.dumps(response_json)


# Delete subnet
def neutron_delete_subnet(env):

    # Retrive token from request
    X_AUTH_TOKEN = env['HTTP_X_AUTH_TOKEN']
    
    site_pattern = re.compile(r'(?<=/subnets/).*')
    match = site_pattern.search(env['PATH_INFO'])
    subnet_id = match.group()   
    
    # Create suffix of service url
    url_suffix = config.get('Neutron', 'neutron_public_interface') + '/v2.0/subnets/'  
    
    res = query_from_DB(AGENT_NEUTRON_ENGINE_CONNECTION, Subnet, Subnet.uuid_agent, subnet_id)
    
    # If subnet does not exist
    if res.count() == 0:
    
        response_message = "Subnet %s could not be found" % subnet_id
        response = {"NeutronError":{"detail":"","message":response_message,"type":"SubnetNotFound"}}
        status_code = '404'
        headers = {'Content-Type': 'application/json'} 
        headers = ast.literal_eval(str(headers)).items()
    
        return status_code, headers, json.dumps(response)
    
    # If subnet exists then delete
    else:
    
        urls = []
        for subnet in res:
            urls.append(subnet.cloud_address + ':' + url_suffix + subnet.uuid_cloud)

        # Get generated threads 
        threads = generate_threads_multicast(X_AUTH_TOKEN, urls, DELETE_request_to_cloud)

        # Launch threads
        for i in range(len(threads)):
	    threads[i].start()

        threads_res = []
    
        # Wait until threads terminate
        for i in range(len(threads)):
	
	    # Parse response from site	
	    res = threads[i].join()
	    threads_res.append(res)
    
        SUCCESS_threads = []
        FAIL_threads = []
        for i in range(len(threads_res)):
        
            # If Network deleted successfully
	    if threads_res[i].status_code == 204:
	   
                # Retrive network uuuid at cloud side
                request_url = vars(threads[i])['_Thread__args'][0]
                match = site_pattern.search(request_url)
                uuid_cloud = match.group()   
            
                # Delete network information in agent DB 
                delete_from_DB(AGENT_NEUTRON_ENGINE_CONNECTION, Subnet, Subnet.uuid_cloud, uuid_cloud)
                SUCCESS_threads.append(threads_res[i])
            else:
                FAIL_threads.append(threads_res[i])

        if len(SUCCESS_threads) != 0:
            response = SUCCESS_threads[0]
            status_code = str(response.status_code)
            headers = ast.literal_eval(str(response.headers)).items()

            return status_code, headers, json.dumps(response.text)
        else:
            response = FAIL_threads[0]
            status_code = str(response.status_code)
            headers = ast.literal_eval(str(response.headers)).items()

            return status_code, headers, json.dumps(response.text)


