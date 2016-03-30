from nova.nova_agent import *
from request import *
from common import *
from db import *
from models import *
import uuid


# List networks
def neutron_list_networks(env):

    # Get all rows of Netowrk object
    network_result = read_all_from_DB(AGENT_DB_ENGINE_CONNECTION, Network)
    
    # If network does not exist
    if len(network_result) == 0:
    
        response_body = {"networks": []}
        return non_exist_response('200', response_body)
        
    # If network exists then delete
    else:
        # Retrive token from request
        X_AUTH_TOKEN = env['HTTP_X_AUTH_TOKEN']
    
        # Create request header
        headers = {'X-Auth-Token': X_AUTH_TOKEN}
        
        # Create suffix of service url
        url_suffix = config.get('Neutron', 'neutron_public_interface') + '/v2.0/networks/'  
        urls = []
        for network in network_result:
            urls.append(network.cloud_address + ':' + url_suffix + network.uuid_cloud)
        
        # Get generated threads 
        threads = generate_threads_multicast(X_AUTH_TOKEN, headers, urls, GET_request_to_cloud)

        # Launch threads
        for i in range(len(threads)):
	    threads[i].start()

        threads_res = []
        # Wait until threads terminate
        for i in range(len(threads)):
	
	    # Parse response from site	
	    res = threads[i].join()
            # If user has right to get access to the resource
            if res.status_code == 200:
                threads_res.append(res)

        response = {'networks':[]}
        
        for network in threads_res:
    
            res = network.json()
            # Network's uuid_cloud
            network_uuid_cloud = res['network']['id']
            result = query_from_DB(AGENT_DB_ENGINE_CONNECTION, Network, columns = [Network.uuid_cloud], keywords = [network_uuid_cloud])

            # Replace network's id by uuid_agent
            res['network']['id'] = result[0].uuid_agent
            
            
            subnets = res['network']['subnets']
            # If network has subnets
            if len(subnets) != 0:
                new_subnets = [] 
                for subnet in subnets:
                    subnet_result = query_from_DB(AGENT_DB_ENGINE_CONNECTION, Subnet, columns = [Subnet.uuid_cloud], keywords = [subnet])
                    new_subnets.append(subnet_result[0].uuid_agent)
                res['network']['subnets'] = new_subnets
            
            new_network_info = add_cloud_info_to_response(result[0].cloud_address, res['network'])
            response['networks'].append(new_network_info)
            
        
        if response['networks'] != 0:
            # Remove duplicate subnets        
            response['networks'] = remove_duplicate_info(response['networks'], 'id')
        

        status_code = str(threads_res[0].status_code)
        headers = threads_res[0].headers
        headers['Content-Length'] = str(len(json.dumps(response)))
        headers = ast.literal_eval(str(headers)).items()

        return status_code, headers, json.dumps(response)



# Show network details
def neutron_show_network_details(env):
	
    site_pattern = re.compile(r'(?<=/v2.0/networks/).*')
    match = site_pattern.search(env['PATH_INFO'])
    network_id = match.group()
            
    network_result = query_from_DB(AGENT_DB_ENGINE_CONNECTION, Network, columns = [Network.uuid_agent], keywords = [network_id])

    # If network does not exist
    if network_result.count() == 0:
        
        message = "Network %s could not be found" % network_id
        response_body = {"NeutronError":{"detail":"","message":message,"type":"NetworkNotFound"}}
        return non_exist_response('404', response_body)
        
    # If network exists then delete
    else:
        # Retrive token from request
        X_AUTH_TOKEN = env['HTTP_X_AUTH_TOKEN']
        
        # Create request header
        headers = {'X-Auth-Token': X_AUTH_TOKEN}

        # Create url
        url = network_result[0].cloud_address + ':' + config.get('Neutron', 'neutron_public_interface') + '/v2.0/networks/' + network_result[0].uuid_cloud

        res = GET_request_to_cloud(url, headers)
    
        response = None
        # Successfully get response from cloud
        if res.status_code == 200:
        
            response = res.json()

            # Replace network's id by uuid_agent
            response['network']['id'] = network_result[0].uuid_agent
            # If network has subnets
            subnets = response['network']['subnets']
            # Replace subnets' ids
            if len(subnets) != 0:
                new_subnets = [] 
                for subnet in subnets:
                    subnet_result = query_from_DB(AGENT_DB_ENGINE_CONNECTION, Subnet, columns = [Subnet.uuid_cloud], keywords = [subnet])
                    new_subnets.append(subnet_result[0].uuid_agent)
                response['network']['subnets'] = new_subnets
            
            # Add cloud info to response 
            for i in range(network_result.count()):
                response['network'] = add_cloud_info_to_response(network_result[i].cloud_address, response['network'])

        else:
            response = res.text

        status_code = str(res.status_code)
        headers = res.headers
        headers['Content-Length'] = str(len(json.dumps(response)))
        headers = ast.literal_eval(str(headers)).items()

        return status_code, headers, json.dumps(response)


# Create network                    
def neutron_create_network(env):
    
    # Retrive token from request
    X_AUTH_TOKEN = env['HTTP_X_AUTH_TOKEN']
    
    # Request data 
    PostData = env['wsgi.input'].read()
    
    # Select site to create network 
    cloud_name, cloud_address = select_site_to_create_object()
    
    # Construct url for creating network
    url = cloud_address + ':' + config.get('Neutron','neutron_public_interface') + env['PATH_INFO'] 
    # Create header
    headers = {'Content-Type': 'application/json', 'X-Auth-Token': X_AUTH_TOKEN}
    
    res = POST_request_to_cloud(url, headers, PostData)
    
    # If network is successfully created in cloud
    if res.status_code == 201:

        # Retrive information from response
        response = res.json()
        tenant_id = response['network']['tenant_id'] 
        network_id = response['network']['id'] 
        network_name = response['network']['name']
        uuid_agent = str(uuid.uuid4())
        #uuid_agent = '8e6df216-d941-4276-8df3-4dee75294d12'
        
        new_network = Network(tenant_id = tenant_id, uuid_agent = uuid_agent, uuid_cloud = network_id, network_name = network_name, cloud_name = cloud_name, cloud_address = cloud_address)
        
        # Add data to DB
        add_to_DB(AGENT_DB_ENGINE_CONNECTION, new_network)

        response['network']['id'] =  uuid_agent
        response['network'] = add_cloud_info_to_response(cloud_address, response['network'])
        
        status_code = str(res.status_code)
        headers = res.headers
        headers['Content-Length'] = str(len(json.dumps(response)))
        headers = ast.literal_eval(str(headers)).items()
        
        return status_code, headers, json.dumps(response)
    
    else:
        status_code = str(res.status_code)
        headers = ast.literal_eval(str(res.headers)).items()

        return status_code, headers, json.dumps(res.json())


# Delete network
def neutron_delete_network(env):
   
    site_pattern = re.compile(r'(?<=/networks/).*')
    match = site_pattern.search(env['PATH_INFO'])
    network_id = match.group()   
    
    res = query_from_DB(AGENT_DB_ENGINE_CONNECTION, Network, columns = [Network.uuid_agent], keywords = [network_id])
    
    # If network does not exist
    if res.count() == 0:
    
        message = "Network %s could not be found" % network_id
        response_body = {"NeutronError":{"detail":"","message":message,"type":"NetworkNotFound"}}
        
        return non_exist_response('404', response_body)
    
    # If network exists then delete
    else:
    
        # Retrive token from request
        X_AUTH_TOKEN = env['HTTP_X_AUTH_TOKEN']
        
        # Create request header
        headers = {'X-Auth-Token': X_AUTH_TOKEN}
    
        # Create suffix of service url
        url_suffix = config.get('Neutron', 'neutron_public_interface') + '/v2.0/networks/'  
        urls = []
        for network in res:
            urls.append(network.cloud_address + ':' + url_suffix + network.uuid_cloud)

        # Get generated threads 
        threads = generate_threads_multicast(X_AUTH_TOKEN, headers, urls, DELETE_request_to_cloud)

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
	   
                # Retrive network uuid_cloud 
                request_url = vars(threads[i])['_Thread__args'][0]
                match = site_pattern.search(request_url)
                uuid_cloud = match.group()   
            
                # Delete subnet information in agent DB 
                delete_from_DB(AGENT_DB_ENGINE_CONNECTION, Subnet, Subnet.network_uuid_cloud, uuid_cloud)
                # Delete network information in agent DB 
                delete_from_DB(AGENT_DB_ENGINE_CONNECTION, Network, Network.uuid_cloud, uuid_cloud)
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

    # Get all rows of Subnet object
    subnet_result = read_all_from_DB(AGENT_DB_ENGINE_CONNECTION, Subnet)
    
    # If network does not exist
    if len(subnet_result) == 0:
    
        response_body = {"subnets": []}
        return non_exist_response('200', response_body)
    
    # If network exists then delete
    else:
        
        # Retrive token from request
        X_AUTH_TOKEN = env['HTTP_X_AUTH_TOKEN']
        
        # Create request header
        headers = {'X-Auth-Token': X_AUTH_TOKEN}
        
        # Create suffix of service url
        url_suffix = config.get('Neutron', 'neutron_public_interface') + '/v2.0/subnets/'  
        urls = []
        for subnet in subnet_result:
            urls.append(subnet.cloud_address + ':' + url_suffix + subnet.uuid_cloud)
        
        # Get generated threads 
        threads = generate_threads_multicast(X_AUTH_TOKEN, headers, urls, GET_request_to_cloud)

        # Launch threads
        for i in range(len(threads)):
	    threads[i].start()

        threads_res = []
    
        # Wait until threads terminate
        for i in range(len(threads)):
	
	    res = threads[i].join()
            # If user has access to the resource
            if res.status_code == 200:
                threads_res.append(res)
    
        response = {'subnets':[]}
        for subnet in threads_res:
    
            res = subnet.json()
            
            # Subnet's uuid_cloud
            subnet_uuid_cloud = res['subnet']['id']
            network_uuid_cloud = res['subnet']['network_id']
            
            # Replace subnet's id by subnet's uuid_agent
            result = query_from_DB(AGENT_DB_ENGINE_CONNECTION, Subnet, columns = [Subnet.uuid_cloud], keywords = [subnet_uuid_cloud])
            res['subnet']['id'] = result[0].uuid_agent
            
            # Replace subnet's network_id by network's uuid_agent
            result = query_from_DB(AGENT_DB_ENGINE_CONNECTION, Network, columns = [Network.uuid_cloud], keywords = [network_uuid_cloud])
            res['subnet']['network_id'] = result[0].uuid_agent
           
            # Add cloud info to response
            new_subnet_info = add_cloud_info_to_response(result[0].cloud_address, res['subnet'])
            response['subnets'].append(new_subnet_info)
         
        if response['subnets'] != 0:
            # Remove duplicate subnets        
            response['subnets'] = remove_duplicate_info(response['subnets'], 'id')
        
        status_code = str(threads_res[0].status_code)
        headers = threads_res[0].headers
        headers['Content-Length'] = str(len(json.dumps(response)))
        headers = ast.literal_eval(str(headers)).items()

        return status_code, headers, json.dumps(response)



# Show subnet details
def neutron_show_subnet_details(env):
            
    site_pattern = re.compile(r'(?<=/v2.0/subnets/).*')
    match = site_pattern.search(env['PATH_INFO'])        
    subnet_id = match.group()

    subnet_result = query_from_DB(AGENT_DB_ENGINE_CONNECTION, Subnet, columns = [Subnet.uuid_agent], keywords = [subnet_id])

    # If network does not exist
    if subnet_result.count() == 0:
        
        message = "Subnet %s could not be found" % network_id
        response_body = {"NeutronError":{"detail":"","message":message,"type":"SubnetNotFound"}}
        return non_exist_response('404', response_body)
    
    # If network exists then delete
    else:
        # Retrive token from request
        X_AUTH_TOKEN = env['HTTP_X_AUTH_TOKEN']
        
        # Create request header
        headers = {'X-Auth-Token': X_AUTH_TOKEN}

        # Create url
        url = subnet_result[0].cloud_address + ':' + config.get('Neutron', 'neutron_public_interface') + '/v2.0/subnets/' + subnet_result[0].uuid_cloud

        # Forward request to the relevant cloud
        res = GET_request_to_cloud(url, headers)
        
        response = None
        # Successfully get response from cloud
        if res.status_code == 200:
            
            response = res.json()
        
            network_uuid_cloud = response['subnet']['network_id']
            # Replace network's id by uuid_agent
            response['subnet']['id'] = subnet_result[0].uuid_agent
        
            # Replace subnet's network_id by network's uuid_agent
            network_result = query_from_DB(AGENT_DB_ENGINE_CONNECTION, Network, columns = [Network.uuid_cloud], keywords = [network_uuid_cloud])
            response['subnet']['network_id'] = network_result[0].uuid_agent
            
            # Add cloud info to response 
            for i in range(subnet_result.count()):
                response['subnet'] = add_cloud_info_to_response(subnet_result[i].cloud_address, response['subnet'])

        else:
            response = res.json()

        # Return response to end-user
        status_code = str(res.status_code)
        headers = res.headers
        headers['Content-Length'] = str(len(json.dumps(response)))
        headers = ast.literal_eval(str(headers)).items()

        return status_code, headers, json.dumps(response)


# Create subnet                    
def neutron_create_subnet(env):
    
    # Request data 
    PostData = env['wsgi.input'].read()
    
    network_id = json.loads(PostData)['subnet']['network_id']
    network_uuid_agent = network_id
    
    # Query from local DB
    res = query_from_DB(AGENT_DB_ENGINE_CONNECTION, Network, columns = [Network.uuid_agent], keywords = [network_id])
    
    # If network does not exist
    if res.count() == 0:
    
        message = "Network %s could not be found" % json.loads(PostData)['subnet']['network_id']
        response_body = {"NeutronError":{"detail":"","message":message,"type":"NetworkNotFound"}}
        return non_exist_response('404', response_body)

    # If network exists
    else:
    
        # Retrive token from request
        X_AUTH_TOKEN = env['HTTP_X_AUTH_TOKEN']
    
        # Create request header
        headers = {'X-Auth-Token': X_AUTH_TOKEN}
    
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
        threads = generate_threads_multicast_with_data(X_AUTH_TOKEN, headers, urls, POST_request_to_cloud, data_set)

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
                add_to_DB(AGENT_DB_ENGINE_CONNECTION, new_subnet)
                
                SUCCESS_threads.append(threads_res[i])
        
            # If subnet failed to be created
            else:
                FAIL_threads.append(threads_res[i])

        if len(SUCCESS_threads) != 0:
        
            response = SUCCESS_threads[0].json()
            subnet_result = query_from_DB(AGENT_DB_ENGINE_CONNECTION, Subnet, columns = [Subnet.uuid_cloud], keywords = [response['subnet']['id']])
            response['subnet']['id'] = subnet_result[0].uuid_agent
            response['subnet']['network_id'] =  network_uuid_agent
            response['subnet'] = add_cloud_info_to_response(subnet_result[0].cloud_address, response['subnet'])
        
            status_code = str(SUCCESS_threads[0].status_code)
            headers = SUCCESS_threads[0].headers
            headers['Content-Length'] = str(len(json.dumps(response)))
            headers = ast.literal_eval(str(headers)).items()

            return status_code, headers, json.dumps(response)

        elif len(FAIL_threads) != 0:
            status_code = str(FAIL_threads[0].status_code)
            headers = ast.literal_eval(str(FAIL_threads[0].headers)).items()
            response = FAIL_threads[0].json()
            
            return status_code, headers, json.dumps(response)


# Delete subnet
def neutron_delete_subnet(env):

    site_pattern = re.compile(r'(?<=/subnets/).*')
    match = site_pattern.search(env['PATH_INFO'])
    subnet_id = match.group()   
    
    res = query_from_DB(AGENT_DB_ENGINE_CONNECTION, Subnet, columns = [Subnet.uuid_agent], keywords = [subnet_id])
    
    # If subnet does not exist
    if res.count() == 0:
    
        message = "Subnet %s could not be found" % subnet_id
        response_body = {"NeutronError":{"detail":"","message":message,"type":"SubnetNotFound"}}
        return non_exist_response('404', response_body)
    
    # If subnet exists then delete
    else:
    
        # Retrive token from request
        X_AUTH_TOKEN = env['HTTP_X_AUTH_TOKEN']
        
        # Create request header
        headers = {'X-Auth-Token': X_AUTH_TOKEN}
        
        # Create suffix of service url
        url_suffix = config.get('Neutron', 'neutron_public_interface') + '/v2.0/subnets/'  
        urls = []
        for subnet in res:
            urls.append(subnet.cloud_address + ':' + url_suffix + subnet.uuid_cloud)

        # Get generated threads 
        threads = generate_threads_multicast(X_AUTH_TOKEN, headers, urls, DELETE_request_to_cloud)

        # Launch threads
        for i in range(len(threads)):
	    threads[i].start()

        threads_res = []
        # Wait until threads terminate
        for i in range(len(threads)):	    
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
                delete_from_DB(AGENT_DB_ENGINE_CONNECTION, Subnet, Subnet.uuid_cloud, uuid_cloud)
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


