#! /usr/bin/env python
# -*- coding: utf-8 -*-
# vim:fenc=utf-8
#
# Copyright © 2016 Xin Han <hxinhan@gmail.com>
#
# Distributed under terms of the MIT license.

import ConfigParser
import _mysql

config = ConfigParser.ConfigParser()
config.read('agent.conf')
DATABASE_PASSWORD = config.get('Database', 'DATABASE_PASSWORD')
print DATABASE_PASSWORD 

#db = _mysql.connect(host="localhost", user="root", passwd="password", db="openstack_agent")
