import ConfigParser
import memcache
import socket
import os
import random

config = ConfigParser.ConfigParser()
config.read('agent.conf')

INTERVAL = int(config.get('CYCLON', 'interval'))
FIXED_SIZE_CACHE = int(config.get('CYCLON', 'fixed_size_cache'))
SHUFFLE_LENGTH = int(config.get('CYCLON', 'shuffle_length'))
RANDOM_WALK_TTL = int(config.get('CYCLON', 'random_walk_TTL'))
MEMCACHED_SERVER_IP = config.get('CYCLON', 'memcached_server_ip')

mc = memcache.Client([MEMCACHED_SERVER_IP], debug=1)

