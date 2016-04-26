#! /usr/bin/env python
# -*- coding: utf-8 -*-

"""

Init local agent database

"""
from db import *
from models import *
from common import get_interface_ip, get_lan_ip 
import ConfigParser
import ast
import uuid

config = ConfigParser.ConfigParser()
config.read('agent.conf')
DATABASE_NAME = config.get('Database', 'DATABASE_NAME')
DATABASE_USERNAME = config.get('Database', 'DATABASE_USERNAME')
DATABASE_PASSWORD = config.get('Database', 'DATABASE_PASSWORD')
SITES = ast.literal_eval(config.get('Clouds','sites'))
AGENT_SITE_NAME = config.get('Agent', 'site')
#AGENT_SITE_IP = SITES[AGENT_SITE_NAME]
AGENT_SITE_IP = 'http://' + get_lan_ip()
# Get introducer's ip address (CYCLON Protocol)
#INTRODUCER_IP = 'http://' + config.get('CYCLON', 'introducer_ip')


# Configuration of DB engine connection
GLANCE_ENGINE_CONNECTION = 'mysql+mysqldb://%s:%s@localhost/glance' % (DATABASE_USERNAME, DATABASE_PASSWORD)
NOVA_ENGINE_CONNECTION = 'mysql+mysqldb://%s:%s@localhost/nova' % (DATABASE_USERNAME, DATABASE_PASSWORD)
NEUTRON_ENGINE_CONNECTION = 'mysql+mysqldb://%s:%s@localhost/neutron' % (DATABASE_USERNAME, DATABASE_PASSWORD)

# Agent DB engine
agentDB_engine = create_engine('mysql+mysqldb://%s:%s@localhost/%s'%(DATABASE_USERNAME, DATABASE_PASSWORD, DATABASE_NAME), echo = False)


# Create tables in database
def create_tables():
    try:
        Base.metadata.create_all(agentDB_engine)
    except exc:
        print exc.message


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
    
    # Read data of subnet from database  
    res = read_from_DB(NEUTRON_ENGINE_CONNECTION, 'subnets', NeutronSubnet)

    # Write to subnet table of agent DB 
    # Create session of subnet table of agetn DB
    DBSession = sessionmaker(bind = agentDB_engine)
    W_session = DBSession()
    
    for subnet in res:
        
        # Check if network already exists in agent DB, if network does not exist in agent DB then add it 
        if len(W_session.query(Subnet).filter_by(uuid_cloud=subnet.id).all()) == 0:
            
            # Synchorize subnet uuid to data table of agent 
            new_subnet = Subnet(tenant_id = subnet.tenant_id, uuid_agent = uuid.uuid4(), uuid_cloud = subnet.id, subnet_name = subnet.name, cloud_name = AGENT_SITE_NAME, cloud_address = AGENT_SITE_IP, network_uuid_cloud = subnet.network_id)
            # Add instance to session
            W_session.add(new_subnet)
    
    network_uuid_cloud = Column(String(36), ForeignKey('network.uuid_cloud'))
    
    # Commit session
    session_commit(W_session)
    
# Synchorize agent table with instance table (instances table in nova DB) in terms of uuid
def Sync_Instance():
   
    # Read data of instance from database
    res = read_from_DB(NOVA_ENGINE_CONNECTION, 'instances', NovaInstance)
    
    # Write to instance table of agent DB 
    # Create session of instance table of agetn DB
    DBSession = sessionmaker(bind = agentDB_engine)
    W_session = DBSession()
    
    for instance in res:
        
        # Check if flavor already exists in agent DB, if flavor does not exist in agent DB then add it 
        if instance.deleted == 0 and len(W_session.query(Instance).filter_by(uuid_cloud=instance.uuid).all()) == 0:
            # Synchorize instance uuid to data table of agent 
            new_instance = Instance(tenant_id = instance.project_id, uuid_cloud = instance.uuid, instance_name = instance.display_name, cloud_name = AGENT_SITE_NAME, cloud_address = AGENT_SITE_IP)
            # Add instance to session
            W_session.add(new_instance)

    # Commit session
    session_commit(W_session)

'''
# Synchorize agent's Neighbor table
def Sync_Neighbor():
   
    print 'introducer: %s' % INTRODUCER_IP
    print 'agent: %s' % AGENT_SITE_IP
    
    # Write to neighbor table of agent DB 
    # Create session of neighbor table of agetn DB
    DBSession = sessionmaker(bind = agentDB_engine)
    W_session = DBSession()
    
    new_neighbor = Neighbor(neighbor_id = uuid.uuid4(), age = 0, cloud_address = AGENT_SITE_IP)
    # Add neighbor to session
    W_session.add(new_neighbor)

    if INTRODUCER_IP != AGENT_SITE_IP:
        new_neighbor = Neighbor(neighbor_id = uuid.uuid4(), age = 0, cloud_address = INTRODUCER_IP)
        # Add neighbor to session
        W_session.add(new_neighbor)

    # Commit session
    session_commit(W_session)
'''   

if __name__ == '__main__':
    create_tables()
    Sync_Image()
    Sync_Flavor()
    Sync_Network()
    Sync_Subnet()
    Sync_Instance()
    #Sync_Neighbor()
