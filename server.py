from eventlet import wsgi
import eventlet
import ConfigParser
from application import application
from models import *

from eventlet.green import socket
from eventlet.green import threading
from eventlet.green import asyncore
eventlet.monkey_patch()

config = ConfigParser.ConfigParser()
config.read('agent.conf')
LISTEN_PORT = int(config.get('Agent','listen_port'))


listener = eventlet.listen(('', LISTEN_PORT))
pool = eventlet.GreenPool(1000)
wsgi.server(listener, application, custom_pool = pool)


# Start agent
#wsgi.server(eventlet.listen(('',LISTEN_PORT)), application)



