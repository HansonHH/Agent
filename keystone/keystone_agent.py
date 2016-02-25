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


###############################################
###########   Identity API v2   ###############
###############################################

# Authenticate users via username and password
def authentication(username,password):
	data = {
		"auth": {"passwordCredentials":{"username": username, "password": password}}
	}
	
	req = urllib2.Request(KEYSTONE_ENDPOINT_PUBLIC+'/v2.0/tokens')
	req.add_header('Content-Type','application/json')
	response = urllib2.urlopen(req,json.dumps(data))


# Verify user's token
def authenticate_token_v2(PostData):
	#print PostData

	url = KEYSTONE_ENDPOINT_PUBLIC + '/v2.0/tokens' 
	req = requests.post(url, data = PostData)
	show_response(inspect.stack()[0][3],res)




###############################################
###########   Identity API v3   ###############
###############################################

def keystone_authentication_v3(env):
	# request data 
	PostData = env['wsgi.input'].read()
	request_json = json.loads(PostData)
	#AUTHENTICATION_METHOD = request_json['auth']['identity']['methods'][0]
	
	SCOPED = None
	response = None

	# Is unscoped or scoped authorization? 
	try:
		SCOPED = request_json['auth']['scope']
		if SCOPED is not None:
			SCOPED = True
	except:
		SCOPED = False
	
	# Construct Keystone's url
	url = KEYSTONE_ENDPOINT_PUBLIC + '/v3/auth/tokens' 
	# Deliver request to Keystone
	res = requests.post(url, data = PostData)
	
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

	# Print response from Keystone
	show_response(inspect.stack()[0][3], res.status_code, user_name, user_id, token, domain_name, domain_id, project_name, project_id, issued_at, expires_at)
	
	# Construct response to client	
	response = response_message(user_name, user_id, token, domain_name, domain_id, project_name, project_id, issued_at, expires_at)

	return response
	
# Print out status code and response from Keystone
def show_response(function_name, status_code, user_name, user_id, token, domain_name, domain_id, project_name, project_id, issued_at, expires_at):
	print '-'*60
	print 'Function Name: %s' % function_name
	print 'Statu Code: %s' % status_code
	if status_code == 400:
		print 'Bad Request!'
	elif status_code == 401:
		print 'Unauthorized!'
	elif status_code == 403:
		print 'Forbidden!'
	elif status_code == 404:
		print 'Not FOund!'
	elif status_code == 405:
		print 'Method Not Allowed!'
	elif status_code == 409:
		print 'Conflict!'
	elif status_code == 413:
		print 'Request Entity Too Large!'
	elif status_code == 415:
		print 'Unsupported Media Type!'
	elif status_code == 503:
		print 'Unavailable!'
	#print response.json()
	print '-'*60

# Construct response to client
def response_message(user_name, user_id, token, domain_name, domain_id, project_name, project_id, issued_at, expires_at):
	
	# Print information at agent side
	'''
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
	'''

	# Construct response to client 	
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
