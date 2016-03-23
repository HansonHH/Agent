#from nova.nova_agent import *
from request import *
from common import *
from db import *
from models import *
import uuid


# List images
def glance_list_images(env):

    # Get all rows of Image object
    result = read_all_from_DB(AGENT_DB_ENGINE_CONNECTION, Image)
    
    # If network does not exist
    if len(result) == 0:
    
        response_body = {"images": []}
        return non_exist_response('200', response_body)
    
    # If network exists then delete
    else:
        # Retrive token from request
        X_AUTH_TOKEN = env['HTTP_X_AUTH_TOKEN']
        
        # Create request header
        headers = {'X-Auth-Token': X_AUTH_TOKEN}
        
        # Create suffix of service url
        url_suffix = config.get('Glance', 'glance_public_interface') + '/v2/images/'  
        urls = []
        for image in result:
            urls.append(image.cloud_address + ':' + url_suffix + image.uuid_cloud)
        
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
    
        response = {'images':[]}
        for image in threads_res:
    
            res = image.json()
            
            # Image's uuid_cloud
            image_uuid_cloud = res['id']
            
            # Replace image's id by image's uuid_agent
            result = query_from_DB(AGENT_DB_ENGINE_CONNECTION, Image, Image.uuid_cloud, image_uuid_cloud)
            res['id'] = result[0].uuid_agent
            
            # Add cloud info to response
            new_image_info = add_cloud_info_to_response(result[0].cloud_address, res)
            response['images'].append(new_image_info)
         
        if response['images'] != 0:
            # Remove duplicate subnets        
            response['images'] = remove_duplicate_info(response['images'], 'id')
        
        status_code = str(threads_res[0].status_code)
        headers = threads_res[0].headers
        headers['Content-Length'] = len(json.dumps(response))
        headers = ast.literal_eval(str(headers)).items()

        return status_code, headers, json.dumps(response)



# Show image details
def glance_show_image_details(env):

    site_pattern = re.compile(r'(?<=/v2/images/).*')
    match = site_pattern.search(env['PATH_INFO'])        
    image_id = match.group()

    image_result = query_from_DB(AGENT_DB_ENGINE_CONNECTION, Image, Image.uuid_agent, image_id)

    # If image does not exist
    if image_result.count() == 0:
        
        message = "Failed to find image %s to delete" % image_id
        response_body = "<html><head><title>404 Not Found</title></head><body><h1>404 Not Found</h1>%s<br/><br/></body></html>" 
        return non_exist_response('404', response_body)
    
    # If image exists then delete
    else:
        # Retrive token from request
        X_AUTH_TOKEN = env['HTTP_X_AUTH_TOKEN']
        
        # Create request header
        headers = {'X-Auth-Token': X_AUTH_TOKEN}

        # Create url
        url = image_result[0].cloud_address + ':' + config.get('Glance', 'glance_public_interface') + '/v2/images/' + image_result[0].uuid_cloud

        # Forward request to the relevant cloud
        res = GET_request_to_cloud(url, headers)
        
        response = None
        # Successfully get response from cloud
        if res.status_code == 200:
            
            response = res.json()
        
            # Replace image's id by uuid_agent
            response['id'] = image_result[0].uuid_agent
            
            # Add cloud info to response 
            for i in range(image_result.count()):
                response = add_cloud_info_to_response(image_result[i].cloud_address, response)
        
        else:
            response = res.text

        # Return response to end-user
        status_code = str(res.status_code)
        headers = res.headers
        headers['Content-Length'] = len(json.dumps(response))
        headers = ast.literal_eval(str(headers)).items()

        return status_code, headers, json.dumps(response)


# Create image                    
def glance_create_image(env):

    # Retrive token from request
    X_AUTH_TOKEN = env['HTTP_X_AUTH_TOKEN']
    
    # Request data 
    PostData = env['wsgi.input'].read()
    
    # Construct url for creating network
    #cloud_name = 'Cloud1'
    #cloud_address = 'http://10.0.1.10'
    cloud_name = 'Cloud3'
    cloud_address = 'http://10.0.1.12'
    
    url = cloud_address + ':' + config.get('Glance','glance_public_interface') + '/v2/images' 
    # Create header
    headers = {'Content-Type': 'application/json', 'X-Auth-Token': X_AUTH_TOKEN}
    
    uuid_agent = None
    post_data_json =  json.loads(PostData)
    # If user specifies image's id
    try:
        uuid_agent = post_data_json['id']
        del post_data_json['id']
    except:
        uuid_agent = str(uuid.uuid4())

    res = POST_request_to_cloud(url, headers, json.dumps(post_data_json))

    # If network is successfully created in cloud
    if res.status_code == 201:

        # Retrive information from response
        response = res.json()
        tenant_id = response['owner'] 
        image_id = response['id'] 
        image_name = response['name']
        
        new_image = Image(tenant_id = tenant_id, uuid_agent = uuid_agent, uuid_cloud = image_id, image_name = image_name, cloud_name = cloud_name, cloud_address = cloud_address)
        
        # Add data to DB
        add_to_DB(AGENT_DB_ENGINE_CONNECTION, new_image)

        status_code = str(res.status_code)
        headers = ast.literal_eval(str(res.headers)).items()
        response['id'] =  uuid_agent

        return status_code, headers, json.dumps(response)
    
    else:
        status_code = str(res.status_code)
        headers = ast.literal_eval(str(res.headers)).items()

        return status_code, headers, json.dumps(res.json())

    

# Upload binary image data                    
def glance_upload_binary_image_data(env):
    
    site_pattern = re.compile(r'(?<=/v2/images/).*(?=/file)')
    match = site_pattern.search(env['PATH_INFO'])        
    image_id = match.group()

    image_result = query_from_DB(AGENT_DB_ENGINE_CONNECTION, Image, Image.uuid_agent, image_id)

    # If image does not exist
    if image_result.count() == 0:
        
        message = "Failed to find image %s to delete" % image_id
        response_body = "<html><head><title>404 Not Found</title></head><body><h1>404 Not Found</h1>%s<br/><br/></body></html>" 
        return non_exist_response('404', response_body)
    
    # If image exists then delete
    else:
        # Retrive token from request
        X_AUTH_TOKEN = env['HTTP_X_AUTH_TOKEN']
    
        # Request data 
        PutData = env['wsgi.input'].read()
        #PutData = env['eventlet.input'].read()

        #data_set.append(PutData)
        data_set = []
    
        # Create header
        headers = {'Content-Type': 'application/octet-stream', 'X-Auth-Token': X_AUTH_TOKEN}

        # Create suffix of service url
        url_suffix = config.get('Glance', 'glance_public_interface') + '/v2/images/'  
        urls = []
        for image in image_result:
            urls.append(image.cloud_address + ':' + url_suffix + image.uuid_cloud + '/file')
            data_set.append(PutData)
        
        # Get generated threads 
        threads = generate_threads_multicast_with_data(X_AUTH_TOKEN, headers, urls, PUT_request_to_cloud, data_set)

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
        
            # If Image deleted successfully
	    if threads_res[i].status_code == 204:
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


# Delete image
def glance_delete_image(env):
    
    site_pattern = re.compile(r'(?<=/images/).*')
    match = site_pattern.search(env['PATH_INFO'])
    image_id = match.group()   
    
    image_result = query_from_DB(AGENT_DB_ENGINE_CONNECTION, Image, Image.uuid_agent, image_id)
    
    # If subnet does not exist
    if image_result.count() == 0:
    
        message = "Failed to find image %s to delete" % image_id
        response_body = "<html><head><title>404 Not Found</title></head><body><h1>404 Not Found</h1>%s<br/><br/></body></html>" 
        return non_exist_response('404', response_body)
    
    # If subnet exists then delete
    else:
    
        # Retrive token from request
        X_AUTH_TOKEN = env['HTTP_X_AUTH_TOKEN']
        
        # Create request header
        headers = {'X-Auth-Token': X_AUTH_TOKEN}
        
        # Create suffix of service url
        url_suffix = config.get('Glance', 'glance_public_interface') + '/v2/images/'  
        urls = []
        for image in image_result:
            urls.append(image.cloud_address + ':' + url_suffix + image.uuid_cloud)

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
        
            # If Image deleted successfully
	    if threads_res[i].status_code == 204:
	   
                # Retrive image uuid at cloud side
                request_url = vars(threads[i])['_Thread__args'][0]
                match = site_pattern.search(request_url)
                uuid_cloud = match.group()   
            
                # Delete network information in agent DB 
                delete_from_DB(AGENT_DB_ENGINE_CONNECTION, Image, Image.uuid_cloud, uuid_cloud)
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
    
    

