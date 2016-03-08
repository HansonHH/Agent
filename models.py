#! /usr/bin/env python
# -*- coding: utf-8 -*-

"""
A file to define data models
"""

from sqlalchemy import *
from sqlalchemy.orm import *
from sqlalchemy.ext.declarative import declarative_base

# Create Base class
Base = declarative_base()

# Define Image class
class Image(Base):

    # Name of table
    __tablename__ = 'image'

    # Data structure of table
    uuid_agent = Column(String(36), primary_key= True)
    uuid_cloud = Column(String(36))
    name = Column(String(40))
    visibility = Column(String(10))
    image_file = Column(String(60))
    owner = Column(String(40))
    protected = Column(Boolean())

    def __repr__(self):
        return "<Image (uuid_agent=%s, uuid_cloud=%s, name=%s, visibility=%s, image_file=%s, owner=%s, protected=%s)>" % (self.uuid_agent, self.uuid_cloud, self.name, self.visibility, self.image_file, self.owner, self.protected)


# Define Flavor class
class Flavor(Base):

    # Name of table
    __tablename__ = 'flavor'

    # Data structure of table
    uuid_agent = Column(String(36), primary_key= True)
    uuid_cloud = Column(String(36))
    name = Column(String(40))
    
    def __repr__(self):
        return "<Flavor (uuid_agent=%s, uuid_cloud=%s, name=%s)>" % (self.uuid_agent, self.uuid_cloud, self.name)


# Define Network class
class Network(Base):

    # Name of table
    __tablename__ = 'network'

    # Data structure of table
    uuid_agent = Column(String(36), primary_key= True)
    uuid_cloud = Column(String(36))
    name = Column(String(40))
    tenant_id = Column(String(36))
    router_external = Column(Boolean())
    admin_state_up = Column(Boolean())
    shared = Column(Boolean())
    
    def __repr__(self):
        return "<Network (uuid_agent=%s, uuid_cloud=%s, name=%s, tenant_id=%s, router_external=%s, admin_state_up=%s, shared=%s)>" % (self.network_uuid_agent, self.network_uuid_cloud, self.name, self.tenant_id, self.router_external, self.admin_state_up, self.shared)


# Define Subnet class
class Subnet(Base):

    # Name of table
    __tablename__ = 'subnet'

    # Data structure of table
    uuid_agent = Column(String(36), primary_key= True)
    uuid_cloud = Column(String(36))
    name = Column(String(40))
    network_uuid_agent = Column(String(40))
    network_uuid_cloud = Column(String(40))
    tenant_id = Column(String(36))
    
    def __repr__(self):
        return "<Subnet (uuid_agent=%s, uuid_cloud=%s, name=%s, network_uuid_agent=%s, network_uuid_cloud=%s, tenant_id=%s)>" % (self.uuid_agent, self.uuid_cloud, self.name, self.network_uuid_agent, self.network_uuid_cloud, self.tenant_id)






