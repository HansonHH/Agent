from nova.nova_agent import *
from request import *

# List images
def glance_list_images(env):
	
    # Retrive token from request
    X_AUTH_TOKEN = env['HTTP_X_AUTH_TOKEN']
	
    # Create suffix of service url
    url_suffix = config.get('Glance', 'glance_public_interface') + '/v2/images' 
    
    # Get generated threads 
    threads = generate_threads(X_AUTH_TOKEN, url_suffix, GET_request_to_cloud)
    
    # Launch threads
    for i in range(len(threads)):
	threads[i].start()
	
    # Initiate response data structure
    json_data = {'images':[]}	

    # Wait until threads terminate
    for i in range(len(threads)):
		
	# Parse response from site	
	parsed_json = json.loads(threads[i].join())

	# Get cloud site information by using regualr expression	
	site_pattern = re.compile(r'(?<=http://).*(?=:)')
	match = site_pattern.search(vars(threads[i])['_Thread__args'][0])
	# IP address of cloud
	site_ip = match.group()
	# Find name of cloud
	site = SITES.keys()[SITES.values().index('http://'+site_ip)]

	# If VM exists in cloud
	if len(parsed_json['images']) != 0:
	    # Recursively look up VMs
	    for i in range(len(parsed_json['images'])):
		parsed_json['images'][i]['site_ip'] = site_ip
		parsed_json['images'][i]['site'] = site
				
		json_data['images'].append(parsed_json['images'][i])
	
    response = json.dumps(json_data)
	
    return response


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
    json_data = {}	

    # Wait until threads terminate
    for i in range(len(threads)):
		
	# Parse response from site	
	try:
	    parsed_json = json.loads(threads[i].join())
	    
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
	
	    return response
			
	except:
	    pass
			
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



