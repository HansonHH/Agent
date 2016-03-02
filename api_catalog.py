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
			
			# Get json data and token	
			response, token = keystone_authentication_v3(env)
			headers = [('Content-Type','application/json'),('X-Subject-Token',token)]	
			# Forward response to end-user
			start_response('200 OK', headers)
			
			return response

		elif PATH_INFO == '':
			pass

	# Compute API v2.1
	elif PATH_INFO.startswith('/v2.1'):
		print '*'*30
		print 'Compute API v2.1 START WITH /v2.1'
		print '*'*30
	
		#pattern = re.compile(r'(?<=/v2.1/).*(?=/servers)')
		#match = pattern.search(env['PATH_INFO'])
		#TENANT_ID = match.group()
		
		# GET request
		if env['REQUEST_METHOD'] == 'GET':
			# List details for servers
			if env['PATH_INFO'].endswith('/detail'):
				print 'ENDSWITH /detail'
				response = nova_list_details_servers(env)
			# List servers
			elif env['PATH_INFO'].endswith('/servers'):
				response = nova_list_servers(env)
			# Show server details
			else:
				response = nova_show_server_details(env)

			headers = [('Content-Type','application/json')]	
			start_response('200 OK', headers)
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
				response = glance_show_image_details(env)
			# List images
			else:
				response = glance_list_images(env)
		
		        headers = [('Content-Type','application/json')]	
		        start_response('200 OK', headers)
                        return response

		# DELETE request	
		if env['REQUEST_METHOD'] == 'DELETE':
			response = glance_delete_image(env)	
			headers = ast.literal_eval(response['headers']).items()
			try:
				if response['status_code'] == 404:
					start_response('404', headers)
				elif response['status_code'] == 204:
					start_response('204', headers)
				return response['text']
			except:
				return response

	# Network API v2.0
	elif PATH_INFO.startswith('/v2.0/networks'):
		print '*'*30
		print 'Network API v2.0 START WITH /v2.0'
		print '*'*30
	
                # GET request
                if env['REQUEST_METHOD'] == 'GET':
                    # List networks
                    if env['PATH_INFO'].endswith('/networks'):
                        response = neutron_list_networks(env)
                    # SHow network details
                    else:
                        response = neutron_show_network_details(env)

		headers = [('Content-Type','application/json')]	
		start_response('200 OK', headers)
                return response




