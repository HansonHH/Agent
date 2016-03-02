from eventlet import wsgi
import eventlet
import ConfigParser
from api_catalog import api_catalog

config = ConfigParser.ConfigParser()
config.read('agent.conf')
LISTEN_PORT = int(config.get('Agent','listen_port'))

# Start agent
wsgi.server(eventlet.listen(('',LISTEN_PORT)), api_catalog)
