from request import *
from common import *
from db import *
from models import *
import uuid
from StringIO import StringIO
import os

# List servers
def nova_list_servers(env):
    
    # Get all rows of Instance object
    server_result = read_all_from_DB(AGENT_DB_ENGINE_CONNECTION, Instance)
    
    # If server does not exist
    if len(server_result) == 0:
    
        response_body = {"servers": []}
        return non_exist_response('200', response_body)
        
    # If server exists then delete
    else:
        # Retrive token from request
        X_AUTH_TOKEN = env['HTTP_X_AUTH_TOKEN']
        
        # Create request header
        headers = {'X-Auth-Token': X_AUTH_TOKEN}

        # Create suffix of service url
        #url_suffix = config.get('Nova', 'nova_public_interface') + '/v2.1/servers/'  
        url_suffix = config.get('Nova', 'nova_public_interface') + env['PATH_INFO'] 
        urls = []
        for server in server_result:
            if server.cloud_address + ':' + url_suffix not in urls:
                urls.append(server.cloud_address + ':' + url_suffix)
            #urls.append(server.cloud_address + ':' + url_suffix)

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
        
        response = {'servers':[]}
        for servers in threads_res:
            
            res = servers.json()
            
            for i in range(len(res['servers'])):
                # Server's uuid_cloud
                server_uuid_cloud = res['servers'][i]['id']
                result = query_from_DB(AGENT_DB_ENGINE_CONNECTION, Instance, columns = [Instance.uuid_cloud], keywords = [server_uuid_cloud])

                new_server_info = add_cloud_info_to_response(result[0].cloud_address, res['servers'][i])
                response['servers'].append(new_server_info)

        if response['servers'] != 0:
            # Remove duplicate subnets        
            response['servers'] = remove_duplicate_info(response['servers'], 'id')
        
        status_code = str(threads_res[0].status_code)
        headers = threads_res[0].headers
        headers['Content-Length'] = len(json.dumps(response))
        headers = ast.literal_eval(str(headers)).items()

        return status_code, headers, json.dumps(response)


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
    
    # Request data 
    PostData = env['wsgi.input'].read()
   
    post_json = json.loads(PostData)

    # Retrive user options from request of creating an VM, if required options are not specified, then send response to end-user
    try:
        res = get_options_from_create_VM_request(post_json)
        instance_name, imageRef, flavorRef, networks = res
    except:
        return res

    # Select site to create VM
    cloud_name, cloud_address = select_site_to_create_object()
     
    # Retrive token from request
    X_AUTH_TOKEN = env['HTTP_X_AUTH_TOKEN']
    
    # Retrive image_id (uuid_agent)
    image_id = None
    if imageRef.startswith('http://'):
        # Retrive tenant id by regular expression 
        image_id_pattern = re.compile(r'(?<=/v2/images/).*')
        match = image_id_pattern.search(imageRef)
        image_id = match.group()
    else:
        image_id = imageRef
    
    # Check if image_id is valid
    image_result = query_from_DB(AGENT_DB_ENGINE_CONNECTION, Image, columns = [Image.uuid_agent], keywords = [image_id])

    # Requested image can not be found
    if image_result.count() == 0:
        message = "Can not fint requested image"
        response_body = {"badRequest" : {"code" : 400, "message": message}}
        return non_exist_response('400', json.dumps(response_body))
    # Requested image can be found
    else:
        # Check if image exist in selected site
        image_exist_result = query_from_DB(AGENT_DB_ENGINE_CONNECTION, Image, columns = [Image.uuid_agent, Image.cloud_address], keywords = [image_id, cloud_address])
    
        # Image does not exist in selected cloud
        if image_exist_result.count() == 0:
            print 'Image does not exist in selected cloud !!!!!!!!!!!!!!'
        
            created_image_uuid_cloud = create_image_in_selected_cloud(X_AUTH_TOKEN, image_result, cloud_name, cloud_address)

            temp_file_path = download_binary_image_data(X_AUTH_TOKEN, image_result)

            upload_res = upload_binary_image_data_to_selected_cloud(X_AUTH_TOKEN, temp_file_path, cloud_address, created_image_uuid_cloud)

            if upload_res:
                print 'upload_res == %s'  % upload_res

                post_json['server']['imageRef'] = created_image_uuid_cloud
        
        # Create the same image in selected cloud
        else:
            print 'Image exists in selected cloud !!!!!!!!!!!!!'
            # Modify imageRef by changing it to image's uuid_cloud
            print image_exist_result[0].uuid_cloud
            post_json['server']['imageRef'] = image_exist_result[0].uuid_cloud


    # Check if network_ids are valid
    invalid_network_uuid_agents = []
    for network_id in networks:
        network_result = query_from_DB(AGENT_DB_ENGINE_CONNECTION, Network, columns = [Network.uuid_agent], keywords = [network_id])
        if network_result.count() == 0:
            invalid_network_uuid_agents.append(network_id)
    
    # Requested network can not be found
    if len(invalid_network_uuid_agents) != 0:
        message = "Netowrk %s could not be found." % ', '.join(invalid_network_uuid_agents)
        response_body = {"badRequest" : {"code" : 400, "message": message}}
        return non_exist_response('400', json.dumps(response_body))
    # Requested network can be found
    else:
        
        network_uuid_clouds = []
        for network_id in networks:
            
            # Check if network exist in selected site
            network_exist_result = query_from_DB(AGENT_DB_ENGINE_CONNECTION, Network, columns = [Network.uuid_agent, Network.cloud_address], keywords = [network_id, cloud_address])
        
            # Network does not exist in selected cloud
            if network_exist_result.count() == 0:
                print 'Network does not exist in selected cloud !!!!!!!!!!!!'
                
                network_result = query_from_DB(AGENT_DB_ENGINE_CONNECTION, Network, columns = [Network.uuid_agent], keywords = [network_id])
                
                # Create network in selected cloud
                created_network_uuid_cloud, subnets = create_network_in_selected_cloud(X_AUTH_TOKEN, network_result, cloud_name, cloud_address)
                
                created_subnet_uuid_clouds = create_subnets_in_selected_cloud(X_AUTH_TOKEN, created_network_uuid_cloud, subnets, cloud_name, cloud_address)
                
                network_dict = {"uuid" : created_network_uuid_cloud}
                network_uuid_clouds.append(network_dict)
                # Create sunbet in selected cloud
            else:
                print 'Network exists in selected cloud !!!!!!!!!!!!!!'
                network_dict = {"uuid" : network_exist_result[0].uuid_cloud}
                network_uuid_clouds.append(network_dict)
    
    
        # Modify networks by changing it to networks' uuid_clouds
        post_json['server']['networks'] = network_uuid_clouds



    # Construct url for creating network
    url = cloud_address + ':' + config.get('Nova','nova_public_interface') + env['PATH_INFO'] 
    # Create header
    headers = {'Content-Type': 'application/json', 'X-Auth-Token': X_AUTH_TOKEN}

    print '!'*60
    print post_json
    print '!'*60
     
    res = POST_request_to_cloud(url, headers, json.dumps(post_json))
    
    # If network is successfully created in cloud
    if res.status_code == 202:

        # Retrive information from response
        response = res.json()
        instance_id = response['server']['id'] 
        # Retrive tenant id
        tenant_id_pattern = re.compile(r'(?<=/v2.1/).*(?=/servers)')
        match = tenant_id_pattern.search(env['PATH_INFO'])
        tenant_id = match.group()   
        
        new_instance = Instance(tenant_id = tenant_id, uuid_cloud = instance_id, instance_name = instance_name, cloud_name = cloud_name, cloud_address = cloud_address)
        
        # Add data to DB
        add_to_DB(AGENT_DB_ENGINE_CONNECTION, new_instance)

        #status_code = str(res.status_code)
        #headers = ast.literal_eval(str(res.headers)).items()
        
        response = add_cloud_info_to_response(cloud_address, response)
        
        # Return response to end-user
        status_code = str(res.status_code)
        headers = res.headers
        headers['Content-Length'] = str(len(json.dumps(response)))
        headers = ast.literal_eval(str(headers)).items()

        return status_code, headers, json.dumps(response)
    
    else:
        status_code = str(res.status_code)
        headers = ast.literal_eval(str(res.headers)).items()

        return status_code, headers, json.dumps(res.json())
    


# Delete image
def nova_delete_server(env):

    server_id_pattern = re.compile(r'(?<=/servers/).*')
    match = server_id_pattern.search(env['PATH_INFO'])
    server_id = match.group()   
    
    instance_result = query_from_DB(AGENT_DB_ENGINE_CONNECTION, Instance, columns = [Instance.uuid_cloud], keywords = [server_id])

    # If subnet does not exist
    if instance_result.count() == 0:
    
        message = "Instance %s could not be found" % server_id
        response_body = {"ItenNotFound":{"code": 404, "message" : message}}
        return non_exist_response('404', json.dumps(response_body))
    
    # If subnet exists then delete
    else:
    
        # Retrive token from request
        X_AUTH_TOKEN = env['HTTP_X_AUTH_TOKEN']
        
        # Create request header
        headers = {'X-Auth-Token': X_AUTH_TOKEN}

        # Construct url for deleting network
        url = instance_result[0].cloud_address + ':' + config.get('Nova','nova_public_interface') + env['PATH_INFO'] 
        
        response = DELETE_request_to_cloud(url, headers)
        
        # If instance deleted successfully
	if response.status_code == 204:
            
            # Delete network information in agent DB 
            delete_from_DB(AGENT_DB_ENGINE_CONNECTION, Instance, Instance.uuid_cloud, instance_result[0].uuid_cloud)

            status_code = str(response.status_code)
            headers = ast.literal_eval(str(response.headers)).items()

            return status_code, headers, json.dumps(response.text)
        else:
            status_code = str(response.status_code)
            headers = ast.literal_eval(str(response.headers)).items()

            return status_code, headers, json.dumps(response.text)


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


# Get user options from request of creating an VM
def get_options_from_create_VM_request(post_json):

    instance_name = None
    imageRef = None
    flavorRef = None
    networks = []
    
    # Check if end-user specified required option name
    try:
        instance_name = post_json['server']['name']
    except:
        message = "Invalid input for field/attribute server. Value: %s. 'name' is a required property" % post_json['server']
        response_body = {"badRequest" : {"code" : 400, "message": message}}
        return non_exist_response('400', json.dumps(response_body))
    
    # Check if end-user specified required option imageRef
    try:
        imageRef = post_json['server']['imageRef']
    except:
        message = "Invalid input for field/attribute server. Value: %s. 'imageRef' is a required property" % post_json['server']
        response_body = {"badRequest" : {"code" : 400, "message": message}}
        return non_exist_response('400', json.dumps(response_body))

    # Check if end-user specified required option flavorRef
    try:
        flavorRef = post_json['server']['flavorRef']
    except:
        message = "Invalid input for field/attribute server. Value: %s. 'flavorRef' is a required property" % post_json['server']
        response_body = {"badRequest" : {"code" : 400, "message": message}}
        return non_exist_response('400', json.dumps(response_body))
    
    # Check if end-user specified optional option networks
    try:
        for network in post_json['server']['networks']:
            networks.append(network['uuid'])
    except:
        
        tenant_id_pattern = re.compile(r'(?<=/v2.1/).*(?=/servers)')
        match = tenant_id_pattern.search(env['PATH_INFO'])
        tenant_id = match.group()

        network_result = query_from_DB(AGENT_DB_ENGINE_CONNECTION, Network, columns = [Network.tenant_id], keywords = [tenant_id])

        if network_result.count() > 1:
        
            message = "Multiple possible networks found, use a Network ID to be more specific"
            response_body = {"conflictingRequest" : {"code" : 409, "message": message}}
            return non_exist_response('409', json.dumps(response_body))
        
        elif network_result.count() == 1:
            
            networks.append(network_result[0].uuid_agent)

    return instance_name, imageRef, flavorRef, networks



def create_image_in_selected_cloud(X_AUTH_TOKEN, image_result, cloud_name, cloud_address):

    print '='*60
   
    # Create header
    headers = {'X-Auth-Token': X_AUTH_TOKEN}
    url = image_result[0].cloud_address + ':' + config.get('Glance', 'glance_public_interface') + '/v2/images/' + image_result[0].uuid_cloud

    # Send request of showing image details to get info of the image
    res = GET_request_to_cloud(url, headers)
        
    res_dict = res.json()
    name = res_dict['name']
    container_format = res_dict['container_format']
    disk_format =  res_dict['disk_format']
    tags = res_dict['tags']
    visibility = res_dict['visibility']
    protected = res_dict['protected']
    min_disk = res_dict['min_disk']
    min_ram = res_dict['min_ram']

    post_dict = {"name":name, "visibility":visibility, "tags":tags, "container_format":container_format, "disk_format":disk_format, "min_disk":min_disk, "min_ram":min_ram, "protected":protected}
    post_json = json.dumps(post_dict)

    url = cloud_address + ':' + config.get('Glance', 'glance_public_interface') + '/v2/images'
    res = POST_request_to_cloud(url, headers, post_json)

    if res.status_code == 201:
        created_image_uuid_cloud = res.json()['id']
        
        new_image = Image(tenant_id = image_result[0].tenant_id, uuid_agent = image_result[0].uuid_agent, uuid_cloud = created_image_uuid_cloud, image_name = image_result[0].image_name, cloud_name = cloud_name, cloud_address = cloud_address)
        
        # Add data to DB
        add_to_DB(AGENT_DB_ENGINE_CONNECTION, new_image)

        return created_image_uuid_cloud

    print '='*60


def download_binary_image_data(X_AUTH_TOKEN, image_result):
    print '-'*60
    # Create header
    headers = {'X-Auth-Token': X_AUTH_TOKEN}
    url = image_result[0].cloud_address + ':' + config.get('Glance', 'glance_public_interface') + '/v2/images/' + image_result[0].uuid_cloud + '/file'

    res = requests.get(url, headers=headers, stream=True)

    if res.status_code == 200:
        # Write binary data to temporay file
        temp_file_path = TEMP_IMAGE_PATH + image_result[0].uuid_agent 
        with open(temp_file_path, 'wb') as f:
            for chunk in res.iter_content(4096):
                f.write(chunk)
        return temp_file_path

    print '-'*60


def upload_binary_image_data_to_selected_cloud(X_AUTH_TOKEN, temp_file_path, cloud_address, created_image_uuid_cloud):

    print '+'*60
    # Create header
    headers = {'Content-Type': 'application/octet-stream', 'X-Auth-Token': X_AUTH_TOKEN}
    url = cloud_address + ':' + config.get('Glance', 'glance_public_interface') + '/v2/images/' + created_image_uuid_cloud + '/file' 

    res = PUT_request_to_cloud(url, headers, temp_file_path)
    
    if res.status_code == 204:
        
        # Delete temporary image file
        try:
            os.remove(temp_file_path)
        except:
            pass
        
        ACTIVE = False
        headers = {'X-Auth-Token': X_AUTH_TOKEN}
        url = cloud_address + ':' + config.get('Glance', 'glance_public_interface') + '/v2/images/' + created_image_uuid_cloud  
        import time
        while not ACTIVE:
            print 'Check if image status is active'
            time.sleep(5)
            res = GET_request_to_cloud(url, headers)
            if res.json()['status'] == "active":
                ACTIVE = True

        
        return True
    else:
        return False
    
    print '+'*60


def create_network_in_selected_cloud(X_AUTH_TOKEN, network_result, cloud_name, cloud_address):
    
    print '~='*60
   
    # Create header
    headers = {'X-Auth-Token': X_AUTH_TOKEN}
    url = network_result[0].cloud_address + ':' + config.get('Neutron', 'neutron_public_interface') + '/v2.0/networks/' + network_result[0].uuid_cloud

    # Send request of showing network details to get info of the network
    res = GET_request_to_cloud(url, headers)
        
    res_dict = res.json()
    print res_dict
    name = res_dict['network']['name']
    admin_state_up = res_dict['network']['admin_state_up']
    shared = res_dict['network']['shared']
    tenant_id = res_dict['network']['tenant_id']
    router_external = res_dict['network']['router:external']
    subnets = res_dict['network']['subnets']

    post_dict = {"network": {"name":name, "admin_state_up":admin_state_up, "shared":shared, "tenant_id":tenant_id, "router:external":router_external}}
    post_json = json.dumps(post_dict)

    print post_json

    url = cloud_address + ':' + config.get('Neutron', 'neutron_public_interface') + '/v2.0/networks'

    print url

    network_res = POST_request_to_cloud(url, headers, post_json)
    
    print network_res.status_code
    print network_res.json()
    if network_res.status_code == 201:
        print '201 !!!!!!!!!!!!!!!!!!!!'
        print network_res.json()
        created_network_uuid_cloud = network_res.json()['network']['id']
        
        print created_network_uuid_cloud

        new_network = Network(tenant_id = network_result[0].tenant_id, uuid_agent = network_result[0].uuid_agent, uuid_cloud = created_network_uuid_cloud, network_name = network_result[0].network_name, cloud_name = cloud_name, cloud_address = cloud_address)
        
        # Add data to DB
        add_to_DB(AGENT_DB_ENGINE_CONNECTION, new_network)

        print subnets
        return created_network_uuid_cloud, subnets
    
    print '~='*60



def create_subnets_in_selected_cloud(X_AUTH_TOKEN, created_network_uuid_cloud, subnets, cloud_name, cloud_address):

    print 'CREATE SUBNETS !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!'
    
    # Create header
    headers = {'X-Auth-Token': X_AUTH_TOKEN}

    created_subnet_uuid_clouds = []

    for subnet_id in subnets:
        print subnet_id
        subnet_result = query_from_DB(AGENT_DB_ENGINE_CONNECTION, Subnet, columns = [Subnet.uuid_cloud], keywords = [subnet_id])
        url = subnet_result[0].cloud_address + ':' + config.get('Neutron', 'neutron_public_interface') + '/v2.0/subnets/' + subnet_result[0].uuid_cloud
    
        # Send request of showing subnet details to get info of the subnet
        res = GET_request_to_cloud(url, headers)

        res_dict = res.json()
        print res_dict
        name = res_dict['subnet']['name']
        network_id = res_dict['subnet']['network_id']
        tenant_id = res_dict['subnet']['tenant_id']
        allocation_pools = res_dict['subnet']['allocation_pools']
        gateway_ip = res_dict['subnet']['gateway_ip']
        ip_version = res_dict['subnet']['ip_version']
        cidr = res_dict['subnet']['cidr']
        enable_dhcp = res_dict['subnet']['enable_dhcp']
        dns_nameservers = res_dict['subnet']['dns_nameservers']
        host_routes = res_dict['subnet']['host_routes']
        try:
            destination = res_dict['subnet']['destination']
        except:
            destination = ''
        try:
            nexthop = res_dict['subnet']['nexthop']
        except:
            nexthop = ''
        ipv6_ra_mode = res_dict['subnet']['ipv6_ra_mode']
        ipv6_address_mode = res_dict['subnet']['ipv6_address_mode']

        #post_dict = {"subnet": {"name":name, "network_id": created_network_uuid_cloud, "tenant_id":tenant_id, "allocation_pools":allocation_pools, "gateway_ip":gateway_ip, "ip_version":ip_version, "cidr":cidr, "enable_dhcp":enable_dhcp, "dns_nameservers":dns_nameservers, "host_routes":host_routes, "destination":destination, "nexthop":nexthop, "ipv6_ra_mode":ipv6_ra_mode, "ipv6_address_mode":ipv6_address_mode}}
        post_dict = {"subnet": {"name":name, "network_id": created_network_uuid_cloud, "tenant_id":tenant_id, "allocation_pools":allocation_pools, "gateway_ip":gateway_ip, "ip_version":ip_version, "cidr":cidr, "enable_dhcp":enable_dhcp, "dns_nameservers":dns_nameservers, "host_routes":host_routes}}

        post_json = json.dumps(post_dict)
        print post_json

        url = cloud_address + ':' + config.get('Neutron', 'neutron_public_interface') + '/v2.0/subnets'
        print url

        subnet_res = POST_request_to_cloud(url, headers, post_json)

        print '&'*30
        print subnet_res.status_code
        print subnet_res.json()

        if subnet_res.status_code == 201:
            created_subnet_uuid_cloud = subnet_res.json()['subnet']['id']

            new_subnet = Subnet(tenant_id = tenant_id, uuid_agent = subnet_result[0].uuid_agent, uuid_cloud = created_subnet_uuid_cloud, subnet_name = name, cloud_name = cloud_name, cloud_address = cloud_address, network_uuid_cloud = created_network_uuid_cloud)
        
            # Add data to DB
            add_to_DB(AGENT_DB_ENGINE_CONNECTION, new_subnet)

            created_subnet_uuid_clouds.append(created_subnet_uuid_cloud)

    print '~'*50
    print created_subnet_uuid_clouds
    print '~'*50
    return created_subnet_uuid_clouds


