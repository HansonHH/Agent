#! /usr/bin/env python
# -*- coding: utf-8 -*-
# vim:fenc=utf-8
#
# Copyright © 2016 Xin Han <hxinhan@gmail.com>
#
# Distributed under terms of the MIT license.

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
    __table__ = 'image'

    # Data structure of table
    image_agent_uuid = Column(String(36), primary_key= True)
    image_cloud_uuid = Column(String(36))


# Define Flavor class
class Flavor(Base):

    # Name of table
    __table__ = 'flavor'

    # Data structure of table
    flavor_agent_uuid = Column(String(36), primary_key= True)
    flavor_cloud_uuid = Column(String(36))

# Define Network class
class Network(Base):

    # Name of table
    __table__ = 'network'

    # Data structure of table
    network_agent_uuid = Column(String(36), primary_key= True)
    network_cloud_uuid = Column(String(36))

# Define Subnet class
class Subnet(Base):

    # Name of table
    __table__ = 'subnet'

    # Data structure of table
    subnet_agent_uuid = Column(String(36), primary_key= True)
    subnet_cloud_uuid = Column(String(36))







