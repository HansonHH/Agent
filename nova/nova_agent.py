from request import *
from common import *
from db import *
from models import *
import uuid
from StringIO import StringIO
import os
import time
import re


def nova_api_version_discovery(env):
        
    # Retrive token from request
    X_AUTH_TOKEN = env['HTTP_X_AUTH_TOKEN']
        
    # Create request header
    headers = {'X-Auth-Token': X_AUTH_TOKEN}
    
    local_site_name = config.get('Agent', 'site')
    local_site_ip = SITES[local_site_name]
   
    # Send a GET request to list API versions
    url = local_site_ip + ':' + config.get('Nova', 'nova_public_interface') + '/' 
    res = GET_request_to_cloud(url, headers)
    response = res.json()

    # Send a GET request to retrive API details
    api_version = ''
    for item in response['versions']:
        if item['status'] == 'CURRENT':
            if item['id'] == 'v2.1':
                api_version = '/v2.1/'
                url = local_site_ip + ':' + config.get('Nova', 'nova_public_interface') + '/v2.1/' 
            elif item['id'] == 'v2.0':
                api_version = '/v2/'
                url = local_site_ip + ':' + config.get('Nova', 'nova_public_interface') + '/v2/' 

    res = GET_request_to_cloud(url, headers)
    response_body = res.json()

    for i in range(len(response_body['version']['links'])):
        try:
            link_type = response_body['version']['links'][i]['type']
        except:
            response_body['version']['links'][i]['href'] = local_site_ip + ':' + config.get('Agent', 'listen_port') + api_version 

    return generate_formatted_response(res, response_body)
    

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
        url_suffix = config.get('Nova', 'nova_public_interface') + env['PATH_INFO'] 
        urls = []
        #for server in server_result:
        for server in server_result:
            if server.cloud_address + ':' + url_suffix not in urls:
                urls.append(server.cloud_address + ':' + url_suffix)
        
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
        
        response_body = {'servers':[]}
        for servers in threads_res:
            
            res = servers.json()
            
            for i in range(len(res['servers'])):
                # Server's uuid_cloud
                server_uuid_cloud = res['servers'][i]['id']
                
                result = query_from_DB(AGENT_DB_ENGINE_CONNECTION, Instance, columns = [Instance.uuid_cloud], keywords = [server_uuid_cloud])

                new_server_info = add_cloud_info_to_response(result[0].cloud_address, res['servers'][i])
                response_body['servers'].append(new_server_info)
            

        if response_body['servers'] != 0:
            # Remove duplicate subnets        
            response_body['servers'] = remove_duplicate_info(response_body['servers'], 'id')
        
        return generate_formatted_response(threads_res[0], response_body)


# List details for servers
def nova_list_details_servers(env):

    # Retrive token from request
    X_AUTH_TOKEN = env['HTTP_X_AUTH_TOKEN']
    
    url_suffix = config.get('Nova', 'nova_public_interface') + env['PATH_INFO']
    
    headers = {'X-Auth-Token': X_AUTH_TOKEN}
    
    urls = []
    for site in SITES.values():
        url = site + ':' + url_suffix
        urls.append(url)

    threads = generate_threads_multicast(X_AUTH_TOKEN, headers, urls, GET_request_to_cloud)

    # Launch threads
    for i in range(len(threads)):
	threads[i].start()
	
    # Initiate response data structure
    response_body = {'servers':[]}	
	
    # Wait until threads terminate
    for i in range(len(threads)):
	
        # Parse response from site	
        try:
	    res = threads[i].join()
            status_code = str(res.status_code)

            # If VM exists in cloud
	    if len(res.json()['servers']) != 0:
	        # Recursively look up VMs
	        for j in range(len(res.json()['servers'])):
		    response_body['servers'].append(res.json()['servers'][j])
        except:
            status_code = str(res.status_code)
		
    return generate_formatted_response(res, response_body)
    

# Show server details
def nova_show_server_details(env):

    site_pattern = re.compile(r'(?<=/servers/).*')
    match = site_pattern.search(env['PATH_INFO'])        
    server_id = match.group()

    server_result = query_from_DB(AGENT_DB_ENGINE_CONNECTION, Instance, columns = [Instance.uuid_cloud], keywords = [server_id])

    # If server does not exist
    if server_result.count() == 0:
        
        message = "Instance %s could not be found" % server_id
        response_body = {"itemNotFound":{"code":"404","message":message}}
        return non_exist_response('404', response_body)
    
    # If server exists then delete
    else:

        # Retrive token from request
        X_AUTH_TOKEN = env['HTTP_X_AUTH_TOKEN']
    
        headers = {'X-Auth-Token': X_AUTH_TOKEN}
        
        # Create url
        url = server_result[0].cloud_address + ':' + config.get('Nova', 'nova_public_interface') + env['PATH_INFO']

        # Forward request to the relevant cloud
        res = GET_request_to_cloud(url, headers)
        
        response_body = None
        # Successfully get response from cloud
        if res.status_code == 200:
            
            response_body = res.json()
            
            # Add cloud info to response 
            #for i in range(image_result.count()):
            #    response = add_cloud_info_to_response(image_result[i].cloud_address, response)
        
        else:
            response_body = res.text
        
        return generate_formatted_response(res, response_body)


# Create VM                    
def nova_create_server(env):

    
    # Request data 
    PostData = env['wsgi.input'].read()
   
    post_json = json.loads(PostData)
    
    #print '@'*80
    #print env
    #print '='*100
    #print post_json
    #print '@'*80

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
        #image_id_pattern = re.compile(r'(?<=/v2/images/).*')
        #match = image_id_pattern.search(imageRef)
        #image_id = match.group()
        image_id = imageRef.split('/')[-1]
    else:
        image_id = imageRef
    
    # Check if image_id is valid
    image_result = query_from_DB(AGENT_DB_ENGINE_CONNECTION, Image, columns = [Image.uuid_agent], keywords = [image_id])

    # Requested image can not be found
    if image_result.count() == 0:
        message = "Can not find requested image"
        response_body = {"badRequest" : {"code" : 400, "message": message}}
        return non_exist_response('400', json.dumps(response_body))
    # Requested image can be found
    else:
        # Check if image exist in selected site
        image_exist_result = query_from_DB(AGENT_DB_ENGINE_CONNECTION, Image, columns = [Image.uuid_agent, Image.cloud_address], keywords = [image_id, cloud_address])
    
        # Image does not exist in selected cloud
        if image_exist_result.count() == 0:
       
            original_image_uuid_cloud = image_result[0].uuid_cloud
            agent_cloud_address = image_result[0].cloud_address

            created_image_uuid_cloud = create_image_in_selected_cloud(X_AUTH_TOKEN, image_result, cloud_name, cloud_address)
            
            # First try to ask another agent to upload binary image data to selected cloud
            try:
            
                upload_res = upload_binary_image_data_to_selected_cloud(X_AUTH_TOKEN, original_image_uuid_cloud, created_image_uuid_cloud, cloud_address, agent_cloud_address)

            # Download binary image data from source cloud and upload to selected cloud
            except:
                
                temp_file_path = download_binary_image_data(X_AUTH_TOKEN, image_result)

                upload_res = upload_temporary_binary_image_data_to_selected_cloud(X_AUTH_TOKEN, temp_file_path, cloud_address, created_image_uuid_cloud)
    
            if upload_res:
                post_json['server']['imageRef'] = created_image_uuid_cloud
        
        # Create the same image in selected cloud
        else:
            # Modify imageRef by changing it to image's uuid_cloud
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
                
                network_result = query_from_DB(AGENT_DB_ENGINE_CONNECTION, Network, columns = [Network.uuid_agent], keywords = [network_id])
                
                # Create network in selected cloud
                created_network_uuid_cloud, subnets = create_network_in_selected_cloud(X_AUTH_TOKEN, network_result, cloud_name, cloud_address)
                
                created_subnet_uuid_clouds = create_subnets_in_selected_cloud(X_AUTH_TOKEN, created_network_uuid_cloud, subnets, cloud_name, cloud_address)
                
                network_dict = {"uuid" : created_network_uuid_cloud}
                network_uuid_clouds.append(network_dict)
                # Create sunbet in selected cloud
            else:
                network_dict = {"uuid" : network_exist_result[0].uuid_cloud}
                network_uuid_clouds.append(network_dict)
    
        # Modify networks by changing it to networks' uuid_clouds
        post_json['server']['networks'] = network_uuid_clouds

    # Construct url for creating network
    url = cloud_address + ':' + config.get('Nova','nova_public_interface') + env['PATH_INFO'] 
    # Create header
    headers = {'Content-Type': 'application/json', 'X-Auth-Token': X_AUTH_TOKEN}

    res = POST_request_to_cloud(url, headers, json.dumps(post_json))
    
    # If VM is successfully created in cloud
    if res.status_code == 202:

        # Retrive information from response
        response_body = res.json()
        instance_id = response_body['server']['id'] 
        # Retrive tenant id
        tenant_id_pattern = re.compile(r'(?<=/v2.1/).*(?=/servers)')
        match = tenant_id_pattern.search(env['PATH_INFO'])
        tenant_id = match.group()   
        
        new_instance = Instance(tenant_id = tenant_id, uuid_cloud = instance_id, instance_name = instance_name, cloud_name = cloud_name, cloud_address = cloud_address)
        
        # Add data to DB
        add_to_DB(AGENT_DB_ENGINE_CONNECTION, new_instance)
        
        response_body = add_cloud_info_to_response(cloud_address, response_body)
        
        return generate_formatted_response(res, response_body)
    
    else:
        
        return generate_formatted_response(res, res.json())


# Delete image
def nova_delete_server(env):

    server_id_pattern = re.compile(r'(?<=/servers/).*')
    match = server_id_pattern.search(env['PATH_INFO'])
    server_id = match.group()   
    
    instance_result = query_from_DB(AGENT_DB_ENGINE_CONNECTION, Instance, columns = [Instance.uuid_cloud], keywords = [server_id])

    # If subnet does not exist
    if instance_result.count() == 0:
    
        message = "Instance %s could not be found" % server_id
        response_body = {"ItemNotFound":{"code": 404, "message" : message}}
        return non_exist_response('404', json.dumps(response_body))
    
    # If subnet exists then delete
    else:
    
        # Retrive token from request
        X_AUTH_TOKEN = env['HTTP_X_AUTH_TOKEN']
        
        # Create request header
        headers = {'X-Auth-Token': X_AUTH_TOKEN}

        # Construct url for deleting network
        url = instance_result[0].cloud_address + ':' + config.get('Nova','nova_public_interface') + env['PATH_INFO'] 
        
        res = DELETE_request_to_cloud(url, headers)
        
        # If instance deleted successfully
	if res.status_code == 204:
            
            # Delete network information in agent DB 
            delete_from_DB(AGENT_DB_ENGINE_CONNECTION, Instance, Instance.uuid_cloud, instance_result[0].uuid_cloud)

        return generate_formatted_response(res, res.text)


# List servers
def nova_list_flavors(env):

    print 'FLAVORS ' *300
    
    # Retrive token from request
    X_AUTH_TOKEN = env['HTTP_X_AUTH_TOKEN']
    
    # Create request header
    headers = {'X-Auth-Token': X_AUTH_TOKEN}
    
    url = config.get('Agent', 'site_ip') + ':' + config.get('Nova', 'nova_public_interface') + env['PATH_INFO']

    print '!'*300
    print url
    
    urls = []
    urls.append(url)
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
		
    response_body = {'flavors':[]}
    for servers in threads_res:
            
        res = servers.json()
	
        for i in range(len(res['flavors'])):
                
            response_body['flavors'].append(res['flavors'][i])
        
    if response_body['flavors'] != 0:
        # Remove duplicate subnets        
        response_body['flavors'] = remove_duplicate_info(response_body['flavors'], 'id')

    import pprint
    pprint.pprint(response_body)
    print threads_res
    print threads_res[0].status_code
        
    return generate_formatted_response(threads_res[0], response_body)
        
        

# List details for flavors
def nova_list_details_flavors(env):
	
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






# Show flavor details
def nova_show_flavor_details(env):

    # Retrive token from request
    X_AUTH_TOKEN = env['HTTP_X_AUTH_TOKEN']
	
    # Create suffix of service url
    url_suffix = config.get('Nova', 'nova_public_interface') + env['PATH_INFO'] 
    
    # Create suffix of service url
    url_suffix = config.get('Nova', 'nova_public_interface') + env['PATH_INFO'] 
    urls = []
    # Get generated threads 
    threads = generate_threads_multicast(X_AUTH_TOKEN, headers, urls, GET_request_to_cloud)
    
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


def download_binary_image_data(X_AUTH_TOKEN, image_result):

    print 'download binary image data '*100

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


# Send a request of uploading binary image data to a agent whose cloud has the responding image file
def upload_binary_image_data_to_selected_cloud(X_AUTH_TOKEN, original_image_uuid_cloud, created_image_uuid_cloud, cloud_address, agent_cloud_address):

    print '%'*100

    # Create header
    headers = {'Content-Type': 'application/json', 'X-Auth-Token': X_AUTH_TOKEN}

    post_dict = {"image": {"original_image_uuid_cloud":original_image_uuid_cloud, "created_image_uuid_cloud":created_image_uuid_cloud, "cloud_address":cloud_address}}
    post_json = json.dumps(post_dict)

    url = agent_cloud_address + ':' + config.get('Agent', 'listen_port') + '/v1/agent/upload_binary_image_data'

    res = POST_request_to_cloud(url, headers, post_json)

    print res.status_code
    print type(res.status_code)


    if res.status_code == 204:
        return True
    else:
        raise Exception('Failed to ask specified agent upload binary image data to selected cloud')
        #return False



def upload_temporary_binary_image_data_to_selected_cloud(X_AUTH_TOKEN, temp_file_path, cloud_address, created_image_uuid_cloud):

    # Create header
    headers = {'Content-Type': 'application/octet-stream', 'X-Auth-Token': X_AUTH_TOKEN}
    url = cloud_address + ':' + config.get('Glance', 'glance_public_interface') + '/v2/images/' + created_image_uuid_cloud + '/file' 

    res = PUT_request_to_cloud(url, headers, temp_file_path)
    
    if res.status_code == 204:
        
        ACTIVE = False
        headers = {'X-Auth-Token': X_AUTH_TOKEN}
        url = cloud_address + ':' + config.get('Glance', 'glance_public_interface') + '/v2/images/' + created_image_uuid_cloud  
        
        while not ACTIVE:
            print 'Check if image status is active'
            time.sleep(5)
            res = GET_request_to_cloud(url, headers)
            if res.json()['status'] == "active":
                ACTIVE = True
        
        return True
    else:
        return False



def create_network_in_selected_cloud(X_AUTH_TOKEN, network_result, cloud_name, cloud_address):
    
    # Create header
    headers = {'X-Auth-Token': X_AUTH_TOKEN}
    url = network_result[0].cloud_address + ':' + config.get('Neutron', 'neutron_public_interface') + '/v2.0/networks/' + network_result[0].uuid_cloud

    # Send request of showing network details to get info of the network
    res = GET_request_to_cloud(url, headers)
        
    res_dict = res.json()
    name = res_dict['network']['name']
    admin_state_up = res_dict['network']['admin_state_up']
    shared = res_dict['network']['shared']
    tenant_id = res_dict['network']['tenant_id']
    router_external = res_dict['network']['router:external']
    subnets = res_dict['network']['subnets']

    post_dict = {"network": {"name":name, "admin_state_up":admin_state_up, "shared":shared, "tenant_id":tenant_id, "router:external":router_external}}
    post_json = json.dumps(post_dict)

    url = cloud_address + ':' + config.get('Neutron', 'neutron_public_interface') + '/v2.0/networks'

    network_res = POST_request_to_cloud(url, headers, post_json)
    
    if network_res.status_code == 201:
        
        created_network_uuid_cloud = network_res.json()['network']['id']
        
        new_network = Network(tenant_id = network_result[0].tenant_id, uuid_agent = network_result[0].uuid_agent, uuid_cloud = created_network_uuid_cloud, network_name = network_result[0].network_name, cloud_name = cloud_name, cloud_address = cloud_address)
        
        # Add data to DB
        add_to_DB(AGENT_DB_ENGINE_CONNECTION, new_network)

        return created_network_uuid_cloud, subnets
    

def create_subnets_in_selected_cloud(X_AUTH_TOKEN, created_network_uuid_cloud, subnets, cloud_name, cloud_address):

    # Create header
    headers = {'X-Auth-Token': X_AUTH_TOKEN}

    created_subnet_uuid_clouds = []

    for subnet_id in subnets:
        subnet_result = query_from_DB(AGENT_DB_ENGINE_CONNECTION, Subnet, columns = [Subnet.uuid_cloud], keywords = [subnet_id])
        url = subnet_result[0].cloud_address + ':' + config.get('Neutron', 'neutron_public_interface') + '/v2.0/subnets/' + subnet_result[0].uuid_cloud
    
        # Send request of showing subnet details to get info of the subnet
        res = GET_request_to_cloud(url, headers)

        res_dict = res.json()
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

        post_dict = {"subnet": {"name":name, "network_id": created_network_uuid_cloud, "tenant_id":tenant_id, "allocation_pools":allocation_pools, "gateway_ip":gateway_ip, "ip_version":ip_version, "cidr":cidr, "enable_dhcp":enable_dhcp, "dns_nameservers":dns_nameservers, "host_routes":host_routes}}

        post_json = json.dumps(post_dict)
        url = cloud_address + ':' + config.get('Neutron', 'neutron_public_interface') + '/v2.0/subnets'
        subnet_res = POST_request_to_cloud(url, headers, post_json)


        if subnet_res.status_code == 201:
            created_subnet_uuid_cloud = subnet_res.json()['subnet']['id']

            new_subnet = Subnet(tenant_id = tenant_id, uuid_agent = subnet_result[0].uuid_agent, uuid_cloud = created_subnet_uuid_cloud, subnet_name = name, cloud_name = cloud_name, cloud_address = cloud_address, network_uuid_cloud = created_network_uuid_cloud)
        
            # Add data to DB
            add_to_DB(AGENT_DB_ENGINE_CONNECTION, new_subnet)

            created_subnet_uuid_clouds.append(created_subnet_uuid_cloud)

    return created_subnet_uuid_clouds


# Nova list images
def nova_list_images(env):

    # Get all rows of Image object
    result = read_all_from_DB(AGENT_DB_ENGINE_CONNECTION, Image)
    
    # If images does not exist
    if len(result) == 0:
        response_body = {"images": []}
        return non_exist_response('404', response_body)
    
    # If images exist
    else:
        # Retrive token from request
        X_AUTH_TOKEN = env['HTTP_X_AUTH_TOKEN']
        
        # Create request header
        headers = {'X-Auth-Token': X_AUTH_TOKEN}
        
        # Create suffix of service url
        url_suffix = config.get('Nova', 'nova_public_interface') + env['PATH_INFO']  
        urls = []
        for image in result:
            #urls.append(image.cloud_address + ':' + url_suffix + image.uuid_cloud)
            urls.append(image.cloud_address + ':' + url_suffix)

        print urls
        
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
        
        response_body = {'images':[]}
        for image in threads_res:
    
            res = image.json()

            import pprint
            #pprint.pprint(res)

            images_list = res['images']
            #print len(images_list)
            print '@'*200
            for i in range(len(images_list)):
                print i
                # Image's uuid_cloud
                image_uuid_cloud = images_list[i]['id']
                print image_uuid_cloud
                print '------------------'
            
                # Replace image's id by image's uuid_agent
                result = query_from_DB(AGENT_DB_ENGINE_CONNECTION, Image, columns = [Image.uuid_cloud], keywords = [image_uuid_cloud])
                #print result[0].uuid_agent

                try:
                    images_list[i]['id'] = result[0].uuid_agent
                except:
                    pass
                
                #for j in range(len(images_list[i]['links'])):
                #    images_list[i]['links'][j]['href'] = result[0].uuid_agent

            #pprint.pprint(images_list)

                response_body['images'].append(images_list[0])

            #pprint.pprint(images_list)
            pprint.pprint(response_body)
            print len(response_body['images'])
            
        ''' 
        if response_body['images'] != 0:
            # Remove duplicate subnets        
            response_body['images'] = remove_duplicate_info(response_body['images'], 'id')
        '''

        return generate_formatted_response(threads_res[0], response_body)


# Nova show image details
def nova_show_image_details(env):

    site_pattern = re.compile(r'(?<=images/).*')
    match = site_pattern.search(env['PATH_INFO'])        
    image_id = match.group()

    image_result = query_from_DB(AGENT_DB_ENGINE_CONNECTION, Image, columns = [Image.uuid_agent], keywords = [image_id])

    # If image does not exist
    if image_result.count() == 0:
        
        message = "Failed to find image %s" % image_id
        response_body = "<html><head><title>404 Not Found</title></head><body><h1>404 Not Found</h1>%s<br/><br/></body></html>" 
        return non_exist_response('404', response_body)
    
    # If image exists then delete
    else:
        # Retrive token from request
        X_AUTH_TOKEN = env['HTTP_X_AUTH_TOKEN']
        
        # Create request header
        headers = {'X-Auth-Token': X_AUTH_TOKEN}

        # Create url
        url = image_result[0].cloud_address + ':' + config.get('Nova', 'nova_public_interface') + '/v2.1/' + image_result[0].tenant_id + '/images/' + image_result[0].uuid_cloud

        # Forward request to the relevant cloud
        res = GET_request_to_cloud(url, headers)
        
        response_body = None

        # Successfully get response from cloud
        if res.status_code == 200:
            
            response_body = res.json()

            # Replace image's id by uuid_agent
            response_body['id'] = image_result[0].uuid_agent
            
            # Add cloud info to response 
            for i in range(image_result.count()):
                response_body = add_cloud_info_to_response(image_result[i].cloud_address, response_body)
        
        else:
            response_body = res.text

        return generate_formatted_response(res, response_body)
