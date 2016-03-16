#from nova.nova_agent import *
from request import *
from common import *

# List images
def glance_list_images(env):
	
    # Retrive token from request
    X_AUTH_TOKEN = env['HTTP_X_AUTH_TOKEN']
	
    # Create suffix of service url
    url_suffix = config.get('Glance', 'glance_public_interface') + env['PATH_INFO'] 
    
    # Get generated threads 
    threads = generate_threads(X_AUTH_TOKEN, url_suffix, GET_request_to_cloud)
    
    # Launch threads
    for i in range(len(threads)):
	threads[i].start()
	
    # Initiate response data structure
    json_data = {'images':[]}	
    headers = [('Content-Type','application/json')]	
    status_code = ''

    # Wait until threads terminate
    for i in range(len(threads)):
		
	# Parse response from site	
        try:

	    response = json.loads(threads[i].join()[0])
            status_code = str(threads[i].join()[1])

	    # If image exists in cloud
	    if len(response['images']) != 0:

	        # Recursively look up images
	        for j in range(len(response['images'])):
                    # Add cloud info to response	            
                    new_response = add_cloud_info_to_response(vars(threads[i])['_Thread__args'][0], response['images'][j])
		    json_data['images'].append(new_response)

        except:
            status_code = str(threads[i].join()[1])

    # Create status code response
    # If there exists at least one image
    if len(json_data['images']) != 0:
        status_code = normal_status_code
        res = json.dumps(json_data)
    # No image exists
    elif len(json_data['images']) == 0:
        res = json.dumps({'servers':[]})

    return (res, status_code, headers)



# Show image details
def glance_show_image_details(env):
	
    # Retrive token from request
    X_AUTH_TOKEN = env['HTTP_X_AUTH_TOKEN']
    
    # Create suffix of service url
    url_suffix = config.get('Glance', 'glance_public_interface') + env['PATH_INFO'] 
    
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
        # If found image
	try:
	    response = json.loads(threads[i].join()[0])
            status_code = str(threads[i].join()[1])
	    # Add cloud info to response 
            response = add_cloud_info_to_response(vars(threads[i])['_Thread__args'][0], response)

            res = json.dumps(response)
            return (res, status_code, headers)
	
        # If not found image	
	except:
            status_code = str(threads[i].join()[1])
            res = json.dumps(threads[i].join()[0])
    
    return (res, status_code, headers)


# Create image                    
def glance_create_image(env):
    
    # Retrive token from request
    X_AUTH_TOKEN = env['HTTP_X_AUTH_TOKEN']
    
    # Request data 
    PostData = env['wsgi.input'].read()
    
    # Construct url for creating network
    url = 'http://10.0.1.11:' + config.get('Glance','glance_public_interface') + env['PATH_INFO'] 
    # Create header
    headers = {'Content-Type': 'application/json', 'X-Auth-Token': X_AUTH_TOKEN}
    
    response = POST_request_to_cloud(url, headers, PostData)
    
    return response


# Upload binary image data                    
def glance_upload_binary_image_data(env):
    
    # Retrive token from request
    X_AUTH_TOKEN = env['HTTP_X_AUTH_TOKEN']
    
    # Request data 
    PutData = env['wsgi.input'].read()
    
    # Construct url for creating network
    url = 'http://10.0.1.11:' + config.get('Glance','glance_public_interface') + env['PATH_INFO'] 

    # Create header
    headers = {'Content-Type': 'application/octet-stream', 'X-Auth-Token': X_AUTH_TOKEN}
    
    response = PUT_request_to_cloud(url, headers, PutData)

    return response


# Delete image
def glance_delete_image(env):
	
    # Retrive token from request
    X_AUTH_TOKEN = env['HTTP_X_AUTH_TOKEN']
    
    # Create suffix of service url
    url_suffix = config.get('Glance', 'glance_public_interface') + env['PATH_INFO'] 
    
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
        # Image delete successfully
	if threads_json[i]['status_code'] == 204:
	    return threads_json[i]
		
    if len(threads_json) != 0:
	return threads_json[0] 
    else:
	return 'Failed to delete image! \r\n'


