import json
#from keystone.keystone_agent import * 
#from nova.nova_agent import * 
#from glance.glance_agent import * 
#from neutron.neutron_agent import * 
from agent import *

# Launch Peer Thread
agent_launch_cyclon_peer_thread()

def application(env, start_response):

    PATH_INFO = env['PATH_INFO']
    REQUEST_METHOD = env['REQUEST_METHOD']
	
    if PATH_INFO.startswith('/v1/agent/cyclon/view_exchange'):
        print '*'*30
        print 'Agent v1.0 CYCLON View Exchange'
        print '*'*30
        
        status_code, headers, response = agent_cyclon_view_exchange(env)
        start_response(status_code, headers)

        print '='*20
        print status_code
        print headers
        print response
        print '='*20

        return response

    if PATH_INFO.startswith('/v1/agent/cyclon/new_peer_join'):
        print '*'*30
        print 'Agent v1.0 CYCLON New Peer Join'
        print '*'*30
        
        status_code, headers, response = agent_cyclon_new_peer_join(env)
        start_response(status_code, headers)

        print '='*20
        print status_code
        print headers
        print response
        print '='*20

        return response


