import json
from keystone.keystone_agent import * 
from nova.nova_agent import * 
from glance.glance_agent import * 
from neutron.neutron_agent import * 
from agent import *

#def api_catalog(env, start_response):
def application(env, start_response):
	
    print env
    PATH_INFO = env['PATH_INFO']
    print '~'*60
    print PATH_INFO
    print '~'*60
	
    # API catalog
    # Identity API v3
    if PATH_INFO.startswith('/v3'):
	print '*'*30
	print 'Identity API v3 START WITH /v3'
	print '*'*30

        # GET request
	if env['REQUEST_METHOD'] == 'GET':
        
            url = 'http://10.0.1.10:5000/v3'
            headers = {'Accept': 'application/json', 'User-Agent': 'python-keystoneclient'}
            res = GET_request_to_cloud('http://10.0.1.10:5000/v3', headers)

            print '='*60
            print res.json()
            print '-'*10
            links = []
            links.append({'href': 'http://10.0.1.11:18090/v3/', 'ref': 'self'})
            response = res.json()
            response['version']['links'] = links
            print headers
            print '-'*10
            print response
            print '='*60
	
            headers = ast.literal_eval(str(res.headers)).items()

	    start_response(str(res.status_code), headers)

            return json.dumps(response)
        
        # POST request
	if env['REQUEST_METHOD'] == 'POST':

            # Authentication and token management (Identity API v3)
            if PATH_INFO == '/v3/auth/tokens':
	    
                res = keystone_authentication_v3(env)
            
                print '!'*100
                #print json.dumps(response.json())
                response = res.json()
                print response['token']['catalog'][3]['endpoints']

                for i in range(9):
                    response['token']['catalog'][3]['endpoints'][i]['url'] = 'http://10.0.1.11:18090/v2.1/98bdf671dfc74d51ba4969f4e963acca'
                
                print '!'*100
                print response['token']['catalog'][3]['endpoints']
                # Shift dictionary to tuple
	        #headers = ast.literal_eval(str(response.headers)).items()
        
                headers = res.headers
                headers['Content-Length'] = str(len(json.dumps(response)))
                headers = ast.literal_eval(str(headers)).items()
        
                # Respond to end user
	        start_response(str(res.status_code), headers)

                return json.dumps(response)

        '''
	# Authentication and token management (Identity API v3)
	if PATH_INFO == '/v3/auth/tokens':
	    
            response = keystone_authentication_v3(env)
            
            # Shift dictionary to tuple
	    headers = ast.literal_eval(str(response.headers)).items()
            # Respond to end user
	    start_response(str(response.status_code), headers)

            return json.dumps(response.json())
        '''


    # Compute API v2.1
    elif PATH_INFO.startswith('/v2.1'):
	print '*'*30
	print 'Compute API v2.1 START WITH /v2.1'
	print '*'*30

        site_pattern = re.compile(r'(?<=/v2.1/).*(?=/servers)')
	match = site_pattern.search(env['PATH_INFO'])
	
        # GET request
	if env['REQUEST_METHOD'] == 'GET':
              
            # Version discovery
            if PATH_INFO.endswith('/v2.1/'):
		status_code, headers, response = nova_api_version_discovery(env)
                
            # List details for servers
	    elif PATH_INFO.endswith('/servers/detail'):
		status_code, headers, response = nova_list_details_servers(env)
	    
            # List servers
	    elif PATH_INFO.endswith('/servers'):
		status_code, headers, response = nova_list_servers(env)
            
            else:
	        # Show server details
                try:
                    site_pattern = re.compile(r'(?<=/servers/).*')
                    match = site_pattern.search(env['PATH_INFO'])        
                    server_id = match.group()
		    status_code, headers, response = nova_show_server_details(env)
                except:
                    print '404 '*100
                    status_code = '404'
                    headers = ''
                    response = ''

            start_response(status_code, headers)
	   
            return response

            '''
            # APIs for flavors
            # List details for flavors
            elif PATH_INFO.endswith('/flavors/detail'):
                response, status_code, headers = nova_list_details_flavors(env)
	    # List flavors
            elif PATH_INFO.endswith('/flavors'):
                response, status_code, headers = nova_list_flavors(env)
	    # Show flavor details
	    else:
		response, status_code, headers = nova_show_flavor_details(env)
	    
            start_response(status_code, headers)
	   
            return response
            '''


            '''
            # APIs for servers
            try:
                res = match.group()
            
                # List details for servers
	        if PATH_INFO.endswith('/servers/detail'):
		    response, status_code, headers = nova_list_details_servers(env)
	        # List servers
	        elif PATH_INFO.endswith('/servers'):
                    print '!'*80
		    response, status_code, headers = nova_list_servers(env)
	        # Show server details
	        else:
		    response, status_code, headers = nova_show_server_details(env)

                start_response(status_code, headers)
            
                return response

            # APIs for flavors
            except:

                print '?'*80

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
            '''
        # POST request
        elif env['REQUEST_METHOD'] == 'POST':
	    
            # Create VM
            if PATH_INFO.endswith('/servers'):

                status_code, headers, response = nova_create_server(env)

            # Create flavor
            elif PATH_INFO.endswith('/flavors'):
                
                status_code, headers, response = nova_create_flavor(env)
            
            start_response(status_code, headers)

            return response
	
        # DELETE request	
        elif env['REQUEST_METHOD'] == 'DELETE':
            
            # API for server
            try:
                res = match.group()
	    
                # Delete server
                status_code, headers, response = nova_delete_server(env)
            
            # API for flavor
            except:
                pass
                # Delete flavor
                status_code, headers, response = nova_delete_flavor(env)
                #response = nova_delete_flavor(env)	
                
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


    elif PATH_INFO.startswith('/v1/agent/upload_binary_image_data'):
        print '*'*30
        print 'Agent v1.0 Upload binary image data'
        print '*'*30

        status_code, headers, response = agent_upload_binary_image_data_to_selected_cloud(env)
        start_response(status_code, headers)

        return response






