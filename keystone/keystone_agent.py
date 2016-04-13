from nova.nova_agent import *
from request import *

config = ConfigParser.ConfigParser()
config.read('agent.conf')
KEYSTONE_ENDPOINT_PUBLIC = config.get('Keystone','site') + ':' + config.get('Keystone','keystone_public_interface')
KEYSTONE_ENDPOINT_ADMIN =  config.get('Keystone','site') + ':' + config.get('Keystone','keystone_admin_interface')
KEYSTONE_ENDPOINT_INTERNAL = config.get('Keystone','site') + ':' + config.get('Keystone','keystone_internal_interface')
AGENT_IP = config.get('Agent','site_ip')


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

    url = KEYSTONE_ENDPOINT_PUBLIC + '/v2.0/tokens' 
    req = requests.post(url, data = PostData)
    show_response(inspect.stack()[0][3],res)


###############################################
###########   Identity API v3   ###############
###############################################

# A function to map Keystone API v3 endpoint t0 agent's identity service ednpoint
def keystone_mapping_api_v3_endpoint(env):
    
    headers = {'Accept': 'application/json', 'User-Agent': 'python-keystoneclient'}

    url = KEYSTONE_ENDPOINT_PUBLIC + '/v3' 
    
    res = GET_request_to_cloud(url, headers)

    response_body = res.json()
    response_body['version']['links'][0]['href'] = 'http://10.0.1.11:18090/v3'
	    
    return generate_formatted_response(res, response_body)


def keystone_authentication_v3(env):
    # request data 
    PostData = env['wsgi.input'].read()

    # Construct Keystone's url
    url = KEYSTONE_ENDPOINT_PUBLIC + '/v3/auth/tokens' 
    # Create header
    headers = {'Content-Type': 'application/json'}
    
    res = POST_request_to_cloud(url, headers, PostData)
   
    # If is scoped authrization
    try:
        is_scoped = res.json()['token']['catalog']
        # Map service endpoints to agent endpoints 
        response_body = endpoints_mapping(res)
    except:
        response_body = res.json()
            
    return generate_formatted_response(res, response_body)
    

# A function to map OpenStack service endpoints to agent service endpoints
def endpoints_mapping(data):

    response = data.json()

    catalog = response['token']['catalog']
    
    for i in range(len(catalog)):
        
        catalog_name = catalog[i]['name']
        
        if catalog_name == 'neutron' or catalog_name == 'glance' or catalog_name == 's3' or catalog_name == 'ec2':
            for j in range(len(catalog[i]['endpoints'])):
                url = catalog[i]['endpoints'][j]['url'] 
                url_split = url.split('/')
                catalog[i]['endpoints'][j]['url'] = AGENT_IP + ':' + config.get('Agent', 'listen_port')

        elif catalog_name == 'nova' or catalog_name == 'nova_legacy':
            for j in range(len(catalog[i]['endpoints'])):
                url = catalog[i]['endpoints'][j]['url'] 
                url_split = url.split('/')
                catalog[i]['endpoints'][j]['url'] = AGENT_IP + ':' + config.get('Agent', 'listen_port') + '/' + url_split[3] + '/' + url_split[4]
        
        elif catalog_name == 'keystone':
            for j in range(len(catalog[i]['endpoints'])):
                url = catalog[i]['endpoints'][j]['url'] 
                url_split = url.split('/')
                catalog[i]['endpoints'][j]['url'] = AGENT_IP + ':' + config.get('Agent', 'listen_port') + '/' + url_split[3]
    
    #import pprint
    #pprint.pprint(response)

    return response

