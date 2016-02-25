from eventlet import wsgi
import eventlet
import os
import json
import requests
import ConfigParser
from keystone.keystone_agent import *
from nova.nova_agent import *

config = ConfigParser.ConfigParser()
config.read('agent.conf')
LISTEN_PORT = int(config.get('Agent','listen_port'))

'''
print os.getenv('OS_PROJECT_DOMAIN_ID')
print os.getenv('OS_USER_DOMAIN_ID')
print os.getenv('OS_PROJECT_NAME')
print os.getenv('OS_TENANT_NAME')
print os.getenv('OS_USERNAME')
print os.getenv('OS_PASSWORD')
print os.getenv('OS_AUTH_URL')
print os.getenv('OS_IDENTITY_API_VERSION')
print os.getenv('OS_IMAGE_API_VERSION')
print os.getenv('OS_TOKEN')
OS_PROJECT_DOMAIN_ID = os.getenv('OS_PROJECT_DOMAIN_ID')
OS_USER_DOMAIN_ID = os.getenv('OS_USER_DOMAIN_ID')
OS_PROJECT_NAME = os.getenv('OS_PROJECT_NAME')
OS_TENANT_NAME = os.getenv('OS_TENANT_NAME')
OS_USERNAME = os.getenv('OS_USERNAME')
OS_PASSWORD = os.getenv('OS_PASSWORD')
OS_AUTH_URL = os.getenv('OS_AUTH_URL')
OS_IDENTITY_API_VERSION = os.getenv('OS_IDENTITY_API_VERSION')
OS_IMAGE_API_VERSION = os.getenv('OS_IMAGE_API_VERSION')
OS_TOKEN = os.getenv('OS_TOKEN')
'''

def hello_world(env, start_response):
	print env
	PATH_INFO = env['PATH_INFO']
	# Retrive json data from user request
	#PostData = env['wsgi.input'].read()
	
	response = None
	
	# API catalog
	# Identity API v2
	if PATH_INFO.startswith('/v2.0'):
		print '*'*30
		print 'Identity API v2 START WITH /v2.0'
		print '*'*30
		
		# Authenticate user's token (Identity API v2)
		if PATH_INFO == '/v2.0/tokens':
			authenticate_token_v2(PostData)
	
	# Identity API v3
	elif PATH_INFO.startswith('/v3'):
		print '*'*30
		print 'Identity API v3 START WITH /v3'
		print '*'*30
		'''
		parsed_json = json.loads(PostData)
		AUTHENTICATION_METHOD = parsed_json['auth']['identity']['methods'][0]
		#print AUTHENTICATION_METHOD
		SCOPED = None
		try:
			SCOPED = parsed_json['auth']['scope']
			if SCOPED is not None:
				SCOPED = True
		except:
			SCOPED = False
		#print SCOPED
		'''

		# Authentication and token management (Identity API v3)
		if PATH_INFO == '/v3/auth/tokens':
			#print '='*60
			
			response = keystone_authentication_v3(env)
			
			'''	
			# Password authentication with unscoped authorization
			if not SCOPED and AUTHENTICATION_METHOD == 'password':
				response = authenticate_password_unscoped_v3(PostData)
			
			# Password authentication with scoped authorization
			elif SCOPED and AUTHENTICATION_METHOD == 'password':
				response = authenticate_password_scoped_v3(PostData)
		     	
			# Token authentication with unscoped authorization	
			elif not SCOPED and AUTHENTICATION_METHOD == 'token':
				response = authenticate_token_unscoped_v3(PostData)	
			
			# Token authentication with scoped authorization
			elif SCOPED and AUTHENTICATION_METHOD == 'token':
				response = authenticate_token_scoped_v3(PostData)
			'''
			#print '='*60
		
		elif PATH_INFO == '':
			pass


	# Compute API v2.1
	elif PATH_INFO.startswith('/v2.1'):
		print '*'*30
		print 'Compute API v2.1 START WITH /v2.1'
		print '*'*30
		
		X_AUTH_TOKEN = env['HTTP_X_AUTH_TOKEN']
		TENANT_ID = '98bdf671dfc74d51ba4969f4e963acca'
		
		# List servers
		if env['REQUEST_METHOD'] == 'GET':
			response = compute_list_servers(X_AUTH_TOKEN, TENANT_ID)
		
	print '*'*150

	start_response('200 OK', [('Content-TYpe','text/plain')])
	#return ['Hello, World!\r\nSecond line\r\n']
	return response



wsgi.server(eventlet.listen(('',LISTEN_PORT)),hello_world)
