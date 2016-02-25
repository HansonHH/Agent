import os
import inspect
import json
import requests
import ConfigParser

config = ConfigParser.ConfigParser()
config.read('agent.conf')
KEYSTONE_ENDPOINT_PUBLIC = config.get('Keystone','site') + ':' + config.get('Keystone','keystone_public_interface')
KEYSTONE_ENDPOINT_ADMIN =  config.get('Keystone','site') + ':' + config.get('Keystone','keystone_admin_interface')
KEYSTONE_ENDPOINT_INTERNAL = config.get('Keystone','site') + ':' + config.get('Keystone','keystone_internal_interface')

# Print out status code and response from Keystone
def show_response(functionname,response):
	print '-'*60
	print 'Function Name: %s' % functionname
	print 'Statu Code: %s' % response.status_code
	if response.status_code == 400:
		print 'Bad Request!'
	elif response.status_code == 401:
		print 'Unauthorized!'
	elif response.status_code == 403:
		print 'Forbidden!'
	elif response.status_code == 404:
		print 'Not FOund!'
	elif response.status_code == 405:
		print 'Method Not Allowed!'
	elif response.status_code == 409:
		print 'Conflict!'
	elif response.status_code == 413:
		print 'Request Entity Too Large!'
	elif response.status_code == 415:
		print 'Unsupported Media Type!'
	elif response.status_code == 503:
		print 'Unavailable!'
	#print response.json()
	print '-'*60


# Authenticate users via username and password
def authentication(username,password):
	data = {
		"auth": {"passwordCredentials":{"username": username, "password": password}}
	}
	
	req = urllib2.Request(KEYSTONE_ENDPOINT_PUBLIC+'/v2.0/tokens')
	req.add_header('Content-Type','application/json')
	response = urllib2.urlopen(req,json.dumps(data))

###############################################
###########   Identity API v2   ###############
###############################################

# Verify user's token
def authenticate_token_v2(PostData):
	#print PostData

	url = KEYSTONE_ENDPOINT_PUBLIC + '/v2.0/tokens' 
	req = requests.post(url, data = PostData)
	show_response(inspect.stack()[0][3],res)




###############################################
###########   Identity API v3   ###############
###############################################
'''
# Password authentication with unscoped authorization
def authenticate_password_unscoped_v3(PostData):
	
	url = KEYSTONE_ENDPOINT_PUBLIC + '/v3/auth/tokens' 
	res = requests.post(url, data = PostData)
	show_response(inspect.stack()[0][3],res)
	
	parsed_json = json.loads(res.text)
	user_name = parsed_json['token']['user']['name']
	user_id = parsed_json['token']['user']['id']
	token = res.headers['X-Subject-Token']
	domain_name = parsed_json['token']['user']['domain']['name']
	domain_id = parsed_json['token']['user']['domain']['id']
	issued_at = parsed_json['token']['issued_at']
	expires_at = parsed_json['token']['expires_at']
	
	response = response_message(user_name, user_id, token, domain_name, domain_id, None, None, issued_at, expires_at)
	print 'user name: %s' % user_name
	print 'user id: %s' % user_id
	print 'token: %s' % token
	print 'domain name: %s' % domain_name
	print 'domain id: %s' % domain_id
	print 'issued_at: %s' % issued_at
	print 'expires_at: %s' % expires_at
	
	return response 
	
# Password authentication with scoped authorization
def authenticate_password_scoped_v3(PostData):
	
	url = KEYSTONE_ENDPOINT_PUBLIC + '/v3/auth/tokens'
	res = requests.post(url, data = PostData)
	show_response(inspect.stack()[0][3],res)
	
	parsed_json = json.loads(res.text)
	user_name = parsed_json['token']['user']['name']
	user_id = parsed_json['token']['user']['id']
	token = res.headers['X-Subject-Token']
	domain_name = parsed_json['token']['user']['domain']['name']
	domain_id = parsed_json['token']['user']['domain']['id']
	project_name = parsed_json['token']['project']['name']
	project_id = parsed_json['token']['project']['id']
	issued_at = parsed_json['token']['issued_at']
	expires_at = parsed_json['token']['expires_at']
	
	response = response_message(user_name, user_id, token, domain_name, domain_id, project_name, project_id, issued_at, expires_at)
	print 'user name: %s' % user_name
	print 'user id: %s' % user_id
	print 'token: %s' % token
	print 'domain name: %s' % domain_name
	print 'domain id: %s' % domain_id
	print 'project name: %s' % project_name
	print 'project id: %s' % project_id
	print 'issued_at: %s' % issued_at
	print 'expires_at: %s' % expires_at
	return response 
# Token authentication with unscoped authorization
def authenticate_token_unscoped_v3(PostData):
	
	url = KEYSTONE_ENDPOINT_PUBLIC + '/v3/auth/tokens' 
	res = requests.post(url, data = PostData)
	show_response(inspect.stack()[0][3],res)
	parsed_json = json.loads(res.text)
	user_name = parsed_json['token']['user']['name']
	user_id = parsed_json['token']['user']['id']
	token = res.headers['X-Subject-Token']
	domain_name = parsed_json['token']['user']['domain']['name']
	domain_id = parsed_json['token']['user']['domain']['id']
	issued_at = parsed_json['token']['issued_at']
	expires_at = parsed_json['token']['expires_at']
	
	response = response_message(user_name, user_id, token, domain_name, domain_id, None, None, issued_at, expires_at)
	print 'user name: %s' % user_name
	print 'user id: %s' % user_id
	print 'token: %s' % token
	print 'domain name: %s' % domain_name
	print 'domain id: %s' % domain_id
	print 'issued_at: %s' % issued_at
	print 'expires_at: %s' % expires_at
	
	return response 
# Token authentication with scoped authorization
def authenticate_token_scoped_v3(PostData):
	url = KEYSTONE_ENDPOINT_PUBLIC + '/v3/auth/tokens' 
	res = requests.post(url, data = PostData)
	show_response(inspect.stack()[0][3],res)
	parsed_json = json.loads(res.text)
	user_name = parsed_json['token']['user']['name']
	user_id = parsed_json['token']['user']['id']
	token = res.headers['X-Subject-Token']
	domain_name = parsed_json['token']['user']['domain']['name']
	domain_id = parsed_json['token']['user']['domain']['id']
	project_name = parsed_json['token']['project']['name']
	project_id = parsed_json['token']['project']['id']
	issued_at = parsed_json['token']['issued_at']
	expires_at = parsed_json['token']['expires_at']
	
	response = response_message(user_name, user_id, token, domain_name, domain_id, project_name, project_id, issued_at, expires_at)
	
	print 'user name: %s' % user_name
	print 'user id: %s' % user_id
	print 'token: %s' % token
	print 'domain name: %s' % domain_name
	print 'domain id: %s' % domain_id
	print 'project name: %s' % project_name
	print 'project id: %s' % project_id
	print 'issued_at: %s' % issued_at
	print 'expires_at: %s' % expires_at
	return response 
'''

def keystone_authentication(env):
	# request data 
	PostData = env['wsgi.input'].read()
	request_json = json.loads(PostData)
	AUTHENTICATION_METHOD = request_json['auth']['identity']['methods'][0]
	
	#print AUTHENTICATION_METHOD
	SCOPED = None
	response = None

	try:
		SCOPED = parsed_json['auth']['scope']
		if SCOPED is not None:
			SCOPED = True
	except:
		SCOPED = False
	
	url = KEYSTONE_ENDPOINT_PUBLIC + '/v3/auth/tokens' 
	res = requests.post(url, data = PostData)
	show_response(inspect.stack()[0][3],res)
	
	# json response from Keystone
	parsed_json = json.loads(res.text)
	
	user_name = parsed_json['token']['user']['name']
	user_id = parsed_json['token']['user']['id']
	token = res.headers['X-Subject-Token']
	domain_name = parsed_json['token']['user']['domain']['name']
	domain_id = parsed_json['token']['user']['domain']['id']
	if SCOPED:
		project_name = parsed_json['token']['project']['name']
		project_id = parsed_json['token']['project']['id']
	else:
		project_name = None
		project_id = None
	issued_at = parsed_json['token']['issued_at']
	expires_at = parsed_json['token']['expires_at']
	
	response = response_message(user_name, user_id, token, domain_name, domain_id, project_name, project_id, issued_at, expires_at)

	'''
	# Password authentication with unscoped authorization
	if not SCOPED and AUTHENTICATION_METHOD == 'password':
		#response = authenticate_password_unscoped_v3(PostData)
		response = response_message(user_name, user_id, token, domain_name, domain_id, None, None, issued_at, expires_at)
			
	# Password authentication with scoped authorization
	elif SCOPED and AUTHENTICATION_METHOD == 'password':
		#response = authenticate_password_scoped_v3(PostData)
		response = response_message(user_name, user_id, token, domain_name, domain_id, project_name, project_id, issued_at, expires_at)
		     	
	# Token authentication with unscoped authorization	
	elif not SCOPED and AUTHENTICATION_METHOD == 'token':
		#response = authenticate_token_unscoped_v3(PostData)	
		response = response_message(user_name, user_id, token, domain_name, domain_id, None, None, issued_at, expires_at)
			
	# Token authentication with scoped authorization
	elif SCOPED and AUTHENTICATION_METHOD == 'token':
		#response = authenticate_token_scoped_v3(PostData)
		response = response_message(user_name, user_id, token, domain_name, domain_id, project_name, project_id, issued_at, expires_at)
	'''
	return response
	
def response_message(user_name, user_id, token, domain_name, domain_id, project_name, project_id, issued_at, expires_at):
	
	print 'user name: %s' % user_name
	print 'user id: %s' % user_id
	print 'token: %s' % token
	print 'domain name: %s' % domain_name
	print 'domain id: %s' % domain_id
	if project_name is not None and project_id is not None:	
		print 'project name: %s' % project_name
		print 'project id: %s' % project_id
	print 'issued_at: %s' % issued_at
	print 'expires_at: %s' % expires_at
	
	response = 'user name: %s\r\n'% user_name
	response = response + 'user id: %s\r\n' % user_id
	response = response + 'token id: %s\r\n' % token
	response = response + 'domain name: %s\r\n' % domain_name
	response = response + 'domain id: %s\r\n' % domain_id
	if project_name is not None and project_id is not None:
		response = response + 'project name: %s\r\n' % project_name
		response = response + 'project id: %s\r\n' % project_id
	response = response + 'issued_at: %s\r\n' % issued_at
	response = response + 'expires_at: %s\r\n' % expires_at
	
	return response 
