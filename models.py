#! /usr/bin/env python
# -*- coding: utf-8 -*-

"""
A file to define data models
"""

from sqlalchemy import *
from sqlalchemy.orm import *
from sqlalchemy.ext.declarative import declarative_base

TABLE_ARGS = {
    #'mysql_engine': 'InnoDB',
    #'mysql_charset': 'utf8'
}



# Create Base class
Base = declarative_base()

# Define Image class
class Image(Base):

    # Name of table
    __tablename__ = 'image'
    # Table configuration
    __table_args__ = TABLE_ARGS
    '''
    __table_args__ = {
            'mysql_engine': 'InnoDB',
            'mysql_charset': 'utf8'
    }
    '''

    # Data structure of table
    uuid_agent = Column(String(36))
    uuid_cloud = Column(String(36), primary_key = True)
    cloud_name = Column(String(40))
    cloud_address = Column(String(40))

    def __repr__(self):
        return "<Image (uuid_agent=%s, uuid_cloud=%s, cloud_name=%s, cloud_address=%s)>" % (self.uuid_agent, self.uuid_cloud, self.cloud_name, self.cloud_address)


# Define Flavor class
class Flavor(Base):

    # Name of table
    __tablename__ = 'flavor'
    # Table configuration
    __table_args__ = TABLE_ARGS
    '''
    __table_args__ = {
            'mysql_engine': 'InnoDB',
            'mysql_charset': 'utf8'
    }
    '''

    # Data structure of table
    uuid_agent = Column(String(36))
    uuid_cloud = Column(String(36), primary_key = True)
    cloud_name = Column(String(40))
    cloud_address = Column(String(40))
    
    def __repr__(self):
        return "<Flavor (uuid_agent=%s, uuid_cloud=%s, cloud_name=%s, cloud_address=%s)>" % (self.uuid_agent, self.uuid_cloud, self.cloud_name, self.cloud_address)


# Define Network class
class Network(Base):

    # Name of table
    __tablename__ = 'network'
    # Table configuration
    __table_args__ = TABLE_ARGS
    '''
    __table_args__ = {
            'mysql_engine': 'InnoDB',
            'mysql_charset': 'utf8'
    }
    '''

    # Data structure of table
    uuid_agent = Column(String(36))
    uuid_cloud = Column(String(36), primary_key = True)
    cloud_name = Column(String(40))
    cloud_address = Column(String(40))
    subnet = relationship("Subnet")
    
    def __repr__(self):
        return "<Network (uuid_agent=%s, uuid_cloud=%s, cloud_name=%s, cloud_address=%s)>" % (self.uuid_agent, self.uuid_cloud, self.cloud_name, self.cloud_address)


# Define Subnet class
class Subnet(Base):

    # Name of table
    __tablename__ = 'subnet'
    # Table configuration
    __table_args__ = TABLE_ARGS
    '''
    __table_args__ = {
            'mysql_engine': 'InnoDB',
            'mysql_charset': 'utf8'
    }
    '''
    
    # Data structure of table
    uuid_agent = Column(String(36))
    uuid_cloud = Column(String(36), primary_key = True)
    cloud_name = Column(String(40))
    cloud_address = Column(String(40))
    network_uuid_cloud = Column(String(36), ForeignKey('network.uuid_cloud'))
    
    def __repr__(self):
        return "<Subnet (uuid_agent=%s, uuid_cloud=%s, cloud_name=%s, cloud_address=%s)>" % (self.uuid_agent, self.uuid_cloud, self.cloud_name, self.cloud_address)



# Data structure of Glance Image
class GlanceImage(object):
    pass

# Data structure of Nova Flavor
class NovaFlavor(object):
    pass

# Data structure of Neutron Network
class NeutronNetwork(object):
    pass

# Data structure of Neutron Subnet
class NeutronSubnet(object):
    pass


