#! /usr/bin/env python
# -*- coding: utf-8 -*-
# vim:fenc=utf-8
#
# Copyright © 2016 Xin Han <hxinhan@gmail.com>
#

import ConfigParser
from sqlalchemy import *
from sqlalchemy.orm import *

engine = create_engine('mysql+mysqldb://root:password@localhost/openstack_agent', pool_recycle=3600, echo= True)

#engine.connect()

metadata = MetaData(engine)

user_table = Table('users', metadata, 
        Column('id', Integer, primary_key=True),
        Column('name', String(40)),
        Column('email', String(120)))

user_table.create()




'''
import MySQLdb

config = ConfigParser.ConfigParser()
config.read('agent.conf')
DATABASE_PASSWORD = config.get('Database', 'DATABASE_PASSWORD')
print DATABASE_PASSWORD 


try:

    con = MySQLdb.connect(host="localhost", user="root", passwd=DATABASE_PASSWORD, db="openstack_agent")
    #con.query("SELECT VERSION()")
    #res = con.use_result()
    #print "MySQL version: %s" % res.fetch_row()[0]
    cur = con.cursor()
    cur.execute("SELECT VERSION()")
    res = cur.fetchone()
    print "MySQL version: %s" % res

except _mysql.Error,e :
    print "Error %d: %s" % (e.args[0], e.args[1])


finally:
    if con:
        con.close()
'''
