import os
import re
import inspect
import json
import requests
import ConfigParser
from nova.thread import ThreadWithReturnValue

config = ConfigParser.ConfigParser()
config.read('agent.conf')
SITES = config.get('Clouds','sites').strip(' ').split(',')
SITES = map (lambda x : x.strip(' '), SITES)
print SITES


# Token authentication with scoped authorization
def compute_list_servers(env):

	# Retrive token from request
	X_AUTH_TOKEN = env['HTTP_X_AUTH_TOKEN']
	# Retrive tenant id by regular expression 
	tenant_id_pattern = re.compile(r'(?<=/v2.1/).*(?=/servers)')
	match = tenant_id_pattern.search(env['PATH_INFO'])
	TENANT_ID = match.group()
	
	# Deliver request to clouds 
	# Create urls of clouds
	urls = []
	for site in SITES:
		url = site + ':' + config.get('Nova','nova_public_interface') + '/v2.1/' + TENANT_ID + '/servers' 
		urls.append(url)
	headers ={'X-Auth-Token':X_AUTH_TOKEN}
	
	# Create threads
	threads = [None] * len(urls)
	for i in range(len(threads)):
		threads[i] = ThreadWithReturnValue(target = request_to_cloud, args=(urls[i], headers,))
	
	# Launch threads
	for i in range(len(threads)):
		threads[i].start()

	response = []	
	# Wait until threads terminate
	for i in range(len(threads)):
		response.append(threads[i].join())
	print response
	print '!'*50

	#show_response(inspect.stack()[0][3],res)
	

def request_to_cloud(url, headers):
	res = requests.get(url, headers = headers)
	return res.text
	#show_response(inspect.stack()[0][3],res)



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
		print 'Bad Method!!'
	print '-'*60
	'''
	parsed_json = json.loads(res.text)
	print 'user name: %s' % parsed_json['token']['user']['name']
	print 'user id: %s' % parsed_json['token']['user']['id']
	print 'token: %s' % res.headers['X-Subject-Token']
	print 'domain name: %s' % parsed_json['token']['user']['domain']['name']
	print 'domain id: %s' % parsed_json['token']['user']['domain']['id']
	print 'project name: %s' % parsed_json['token']['project']['name']
	print 'project id: %s' % parsed_json['token']['project']['id']
	print 'issued_at: %s' % parsed_json['token']['issued_at']
	print 'expires_at: %s' % parsed_json['token']['expires_at']
	'''
