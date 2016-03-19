#! /usr/bin/env python
# -*- coding: utf-8 -*-
# vim:fenc=utf-8
#

"""

Init local agent database

"""
from db import *
import ConfigParser
from models import *
import ast
import uuid

config = ConfigParser.ConfigParser()
config.read('agent.conf')
DATABASE_NAME = config.get('Database', 'DATABASE_NAME')
DATABASE_USERNAME = config.get('Database', 'DATABASE_USERNAME')
DATABASE_PASSWORD = config.get('Database', 'DATABASE_PASSWORD')
SITES = ast.literal_eval(config.get('Clouds','sites'))
AGENT_SITE_NAME = config.get('Agent', 'site')
AGENT_SITE_IP = SITES[AGENT_SITE_NAME]

# Configuration of DB engine connection
GLANCE_ENGINE_CONNECTION = 'mysql+mysqldb://%s:%s@localhost/glance' % (DATABASE_USERNAME, DATABASE_PASSWORD)
NOVA_ENGINE_CONNECTION = 'mysql+mysqldb://%s:%s@localhost/nova' % (DATABASE_USERNAME, DATABASE_PASSWORD)
NEUTRON_ENGINE_CONNECTION = 'mysql+mysqldb://%s:%s@localhost/neutron' % (DATABASE_USERNAME, DATABASE_PASSWORD)

# Agent DB engine
agentDB_engine = create_engine('mysql+mysqldb://%s:%s@localhost/%s'%(DATABASE_USERNAME, DATABASE_PASSWORD, DATABASE_NAME), echo = False)



# Synchorize agent table with glance (images talbe in glance DB) in terms of uuid
def Sync_Image():
    
    # Read data of image from database  
    res = read_from_DB(GLANCE_ENGINE_CONNECTION, 'images', GlanceImage)

    # Write to image table of agent DB 
    # Create session of image table of agetn DB
    DBSession = sessionmaker(bind = agentDB_engine)
    W_session = DBSession()
    
    for image in res:
        
        # Check if image already exists in agent DB, if image does not exist in agent DB then add it 
        if image.status == "active" and len(W_session.query(Image).filter_by(uuid_cloud=image.id).all()) == 0:
            # Synchorize image uuid to data table of agent 
            new_image = Image(tenant_id = image.owner, uuid_agent = uuid.uuid4(), uuid_cloud = image.id, image_name = image.name, cloud_name = AGENT_SITE_NAME, cloud_address = AGENT_SITE_IP)
            # Add instance to session
            W_session.add(new_image)

    # Commit session
    session_commit(W_session)


# Synchorize agent table with flavor table (instance_types table in nova DB) in terms of uuid
def Sync_Flavor():
   
    # Read data of flavor from database  
    res = read_from_DB(NOVA_ENGINE_CONNECTION, 'instance_types', NovaFlavor)

    # Write to image table of agent DB 
    # Create session of image table of agetn DB
    DBSession = sessionmaker(bind = agentDB_engine)
    W_session = DBSession()
    
    for flavor in res:
        
        # Check if flavor already exists in agent DB, if flavor does not exist in agent DB then add it 
        if flavor.deleted == 0 and len(W_session.query(Flavor).filter_by(uuid_cloud=flavor.flavorid).all()) == 0:
            # Synchorize flavor uuid to data table of agent 
            new_flavor = Flavor(uuid_agent = uuid.uuid4(), uuid_cloud = flavor.flavorid, flavor_name = flavor.name, cloud_name = AGENT_SITE_NAME, cloud_address = AGENT_SITE_IP)
            # Add instance to session
            W_session.add(new_flavor)

    # Commit session
    session_commit(W_session)
    

   
# Synchorize agent table with network table (networks table in neutron DB) in terms of uuid
def Sync_Network():
    
    # Read data of network from database  
    res = read_from_DB(NEUTRON_ENGINE_CONNECTION, 'networks', NeutronNetwork)
   
    # Write to subnet table of agent DB 
    # Create session of subnet table of agetn DB
    DBSession = sessionmaker(bind = agentDB_engine)
    W_session = DBSession()
    
    for network in res:
        
        # Check if network already exists in agent DB, if network does not exist in agent DB then add it 
        if network.status == 'ACTIVE' and len(W_session.query(Network).filter_by(uuid_cloud=network.id).all()) == 0:
            # Synchorize subnet uuid to data table of agent 
            new_network = Network(tenant_id = network.tenant_id, uuid_agent = uuid.uuid4(), uuid_cloud = network.id, network_name = network.name, cloud_name = AGENT_SITE_NAME, cloud_address = AGENT_SITE_IP)
            # Add instance to session
            W_session.add(new_network)

    # Commit session
    session_commit(W_session)
    

# Synchorize agent table with subnet table (subnets table in neutron DB) in terms of uuid
def Sync_Subnet():
