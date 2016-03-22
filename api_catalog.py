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

        site_pattern = re.compile(r'(?<=/v2.1/).*(?=/servers)')
	match = site_pattern.search(env['PATH_INFO'])
	
        # GET request
	if env['REQUEST_METHOD'] == 'GET':
        
            # APIs for servers
            try:
                res = match.group()
            
                # List details for servers
	        if PATH_INFO.endswith('/servers/detail'):
		    response, status_code, headers = nova_list_details_servers(env)
	        # List servers
	        elif PATH_INFO.endswith('/servers'):
		    response, status_code, headers = nova_list_servers(env)
	        # Show server details
	        else:
		    response, status_code, headers = nova_show_server_details(env)

            # APIs for flavors
            except:
                # List details for flavors
                if PATH_INFO.endswith('/flavors/detail'):
                    response, status_code, headers = nova_list_details_flavors(env)
	        # List flavors
                elif PATH_INFO.endswith('/flavors'):
                    response, status_code, headers = nova_list_flavors(env)
	        # Show flavor details
	        else:
		    response, status_code, headers = nova_show_flavor_details(env)
	    
            start_response(status_code, headers)
	   
            return response
            
        # POST request
        elif env['REQUEST_METHOD'] == 'POST':
	    
            # Create VM
            if PATH_INFO.endswith('/servers'):

                response = nova_create_server(env)

            # Create flavor
            elif PATH_INFO.endswith('/flavors'):
                
                response = nova_create_flavor(env)
                
            # Shift dictionary to tuple
	    headers = ast.literal_eval(str(response.headers)).items()
            # Respond to end user
	    start_response(str(response.status_code), headers)
            
            return response
	
        # DELETE request	
        elif env['REQUEST_METHOD'] == 'DELETE':
            
            # API for server
            try:
                res = match.group()
	    
                # Delete server
                response = nova_delete_server(env)	
            
            # API for flavor
            except:
                # Delete flavor
                response = nova_delete_flavor(env)	
                
            # Shift dictionary to tuple
	    headers = ast.literal_eval(response['headers']).items()
            # Respond to end user    
            start_response(str(response['status_code']), headers)
            
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
		status_code, headers, response = glance_show_image_details(env)
	    # List images
	    else:
		status_code, headers, response = glance_list_images(env)
		
	    start_response(status_code, headers)
            return response

        # POST request
        elif env['REQUEST_METHOD'] == 'POST':
            # Create image
            status_code, headers, response = glance_create_image(env)
            start_response(status_code, headers)

            return response

        # PUT request
        elif env['REQUEST_METHOD'] == 'PUT':
            #response = glance_upload_binary_image_data(env)
            
            # Shift dictionary to tuple
	    #headers = ast.literal_eval(str(response.headers)).items()
            # Respond to end user
	    #start_response(str(response.status_code), headers)

            #return response
            
            # Upload binary image data
            status_code, headers, response = glance_upload_binary_image_data(env)
            start_response(status_code, headers)

            return response

	# DELETE request	
        elif env['REQUEST_METHOD'] == 'DELETE':
	    # Delete image
            status_code, headers, response = glance_delete_image(env)
            start_response(status_code, headers)

            return response

    # Network API v2.0
    # Network
    elif PATH_INFO.startswith('/v2.0/networks'):
	print '*'*30
	print 'Network API v2.0 START WITH /v2.0'
	print '*'*30
	
        # GET request
        if env['REQUEST_METHOD'] == 'GET':
             
            # List networks
            if env['PATH_INFO'].endswith('/networks'):
                
                status_code, headers, response = neutron_list_networks(env)
                start_response(status_code, headers)

                return response
            
            # Show network details
            else:
	        status_code, headers, response = neutron_show_network_details(env)
                start_response(status_code, headers)

                return response

        # POST request
        elif env['REQUEST_METHOD'] == 'POST':
            
            status_code, headers, response = neutron_create_network(env)
            start_response(status_code, headers)

            return response

	# DELETE request	
	elif env['REQUEST_METHOD'] == 'DELETE':
            
            status_code, headers, response = neutron_delete_network(env)
            start_response(status_code, headers)

            return response

    # Subnet
    elif PATH_INFO.startswith('/v2.0/subnets'):
        print '*'*30
        print 'Network API (Subnets) v2.0 START WITH /v2.0'
        print '*'*30
        
        # GET request
        if env['REQUEST_METHOD'] == 'GET':
            
            # List subnets
            if env['PATH_INFO'].endswith('/subnets'):
                
                status_code, headers, response = neutron_list_subnets(env)
                start_response(status_code, headers)

                return response
            
            # Show network details
            else:
	        status_code, headers, response = neutron_show_subnet_details(env)
                start_response(status_code, headers)

                return response
                    
            '''
            site_pattern = re.compile(r'(?<=/v2.0/subnets/).*')
            match = site_pattern.search(env['PATH_INFO'])        
            subnet_id = match.group()
            '''

        # POST request
        elif env['REQUEST_METHOD'] == 'POST':

            status_code, headers, response = neutron_create_subnet(env)
            start_response(status_code, headers)

            return response


	# DELETE request	
	elif env['REQUEST_METHOD'] == 'DELETE':
            
            status_code, headers, response = neutron_delete_subnet(env)
            start_response(status_code, headers)

            return response
            



