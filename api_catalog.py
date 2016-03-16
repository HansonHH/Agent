import json
from keystone.keystone_agent import *
from nova.nova_agent import *
from glance.glance_agent import *
from neutron.neutron_agent import *


def api_catalog(env, start_response):
	
    print env
    PATH_INFO = env['PATH_INFO']
	
    # API catalog

    # Identity API v3
    if PATH_INFO.startswith('/v3'):
	print '*'*30
	print 'Identity API v3 START WITH /v3'
	print '*'*30

	# Authentication and token management (Identity API v3)
	if PATH_INFO == '/v3/auth/tokens':
	    
            response = keystone_authentication_v3(env)
            
            # Shift dictionary to tuple
	    headers = ast.literal_eval(str(response.headers)).items()
            # Respond to end user
	    start_response(str(response.status_code), headers)

            return json.dumps(response.json())
            
    # Compute API v2.1
    elif PATH_INFO.startswith('/v2.1'):
	print '*'*30
	print 'Compute API v2.1 START WITH /v2.1'
	print '*'*30
	
	# GET request
	if env['REQUEST_METHOD'] == 'GET':
	    # List details for servers
	    if PATH_INFO.endswith('/detail'):
		response, status_code, headers = nova_list_details_servers(env)
	    # List servers
	    elif PATH_INFO.endswith('/servers'):
		response, status_code, headers = nova_list_servers(env)
	    # Show server details
	    else:
		#response = nova_show_server_details(env)
		response, status_code, headers = nova_show_server_details(env)

	    start_response(status_code, headers)
	    
            return response
	
    # Image API v2
    elif PATH_INFO.startswith('/v2/'):
	print '*'*30
	print 'Image API v2 START WITH /v2'
	print '*'*30

	# GET request
	if env['REQUEST_METHOD'] == 'GET':
	    # Show image details
	    if PATH_INFO.startswith('/v2/images/'):
		#response = glance_show_image_details(env)
		response, status_code, headers = glance_show_image_details(env)
	    # List images
	    else:
		response, status_code, headers = glance_list_images(env)
		
	    start_response(status_code, headers)
            return response

        # POST request
        elif env['REQUEST_METHOD'] == 'POST':
            # Create image
            response = glance_create_image(env)
            
            # Shift dictionary to tuple
	    headers = ast.literal_eval(str(response.headers)).items()
            # Respond to end user
	    start_response(str(response.status_code), headers)
            
            return response

        # PUT request
        elif env['REQUEST_METHOD'] == 'PUT':
            # Upload binary image data
            response = glance_upload_binary_image_data(env)
            
            # Shift dictionary to tuple
	    headers = ast.literal_eval(str(response.headers)).items()
            # Respond to end user
	    start_response(str(response.status_code), headers)

            return response

	# DELETE request	
        elif env['REQUEST_METHOD'] == 'DELETE':
	    # Delete image
            response = glance_delete_image(env)	
            
            # Shift dictionary to tuple
	    headers = ast.literal_eval(response['headers']).items()
            # Respond to end user
	    start_response(str(response['status_code']), headers)
            return response

    # Network API v2.0
    # Network
    elif PATH_INFO.startswith('/v2.0/networks'):
	print '*'*30
	print 'Network API v2.0 START WITH /v2.0'
	print '*'*30
	
        # GET request
        if env['REQUEST_METHOD'] == 'GET':
		    
            site_pattern = re.compile(r'(?<=/v2.0/networks/).*')
	    match = site_pattern.search(env['PATH_INFO'])
                    
            try:
		# network id 
		network_id = match.group()
                # Show network details
		response, status_code, headers = neutron_show_network_details(env)
            except:
                # List networks
		response, status_code, headers = neutron_list_networks(env)
        
	    start_response(status_code, headers)
            return response
		
        # POST request
        elif env['REQUEST_METHOD'] == 'POST':

            response = neutron_create_network(env)
            # Shift dictionary to tuple
	    headers = ast.literal_eval(str(response.headers)).items()
            # Respond to end user
	    start_response(str(response.status_code), headers)

            return json.dumps(response.json())


	# DELETE request	
	elif env['REQUEST_METHOD'] == 'DELETE':
            response = neutron_delete_network(env)
	    
            headers = ast.literal_eval(response['headers']).items()
	    start_response(str(response['status_code']), headers)
            
            return response


    # Subnet
    elif PATH_INFO.startswith('/v2.0/subnets'):
        print '*'*30
        print 'Network API v2.0 START WITH /v2.0'
        print '*'*30
        
        # GET request
        if env['REQUEST_METHOD'] == 'GET':
                    
            site_pattern = re.compile(r'(?<=/v2.0/subnets/).*')
            match = site_pattern.search(env['PATH_INFO'])
                    
            try:
                # network id 
                subnet_id = match.group()
                # Show subnet details
		response, status_code, headers = neutron_show_subnet_details(env)
            except:
                # List subnets
		response, status_code, headers = neutron_list_subnets(env)
        
	    start_response(status_code, headers)
            return response
        
        # POST request
        elif env['REQUEST_METHOD'] == 'POST':

            response = neutron_create_subnet(env)
            # Shift dictionary to tuple
	    headers = ast.literal_eval(str(response.headers)).items()
            # Respond to end user
	    start_response(str(response.status_code), headers)

            return json.dumps(response.json())
        



