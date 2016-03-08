#! /usr/bin/env python
# -*- coding: utf-8 -*-
# vim:fenc=utf-8
#
# Copyright © 2016 Xin Han <hxinhan@gmail.com>
#
'''
A file to initiate databse
'''

import ConfigParser
from models import *
import sqlalchemy.exc

config = ConfigParser.ConfigParser()
config.read('agent.conf')
DATABASE_NAME = config.get('Database', 'DATABASE_NAME')
DATABASE_USERNAME = config.get('Database', 'DATABASE_USERNAME')
DATABASE_PASSWORD = config.get('Database', 'DATABASE_PASSWORD')

engine = create_engine('mysql+mysqldb://%s:%s@localhost/%s'%(DATABASE_USERNAME, DATABASE_PASSWORD, DATABASE_NAME), pool_recycle=3600, echo= True)

# Create tables in database
def create_tables():
    try:
        Base.metadata.create_all(engine)
    except exc:
        print exc.message



def create_test():
    DBSession = sessionmaker(bind=engine)

    session = DBSession()
    
    new_image = Image(uuid_agent='agent_2', uuid_cloud='cloud_2', name='image2', visibility='public', image_file='/v2/images/1bea47ed-f6a9-463b-b423-14b9cca9ad27/file', owner='5ef70662f8b34079a6eddb8da9d75fe8', protected=False)

    try:
        session.add(new_image)
        session.commit()
    except sqlalchemy.exc.IntegrityError, exc:
        reason = exc.message
        if reason.endswith('is not unique'):
            print "%s already exists" % exc.params[0]
            session.rollback()
    finally:
        session.close()


#create_test()



if __name__ == '__main__':
    #create_tables()
    create_test()


