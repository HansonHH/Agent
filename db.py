#! /usr/bin/env python
# -*- coding: utf-8 -*-
# vim:fenc=utf-8
#
# Copyright © 2016 Xin Han <hxinhan@gmail.com>
#
'''

A file to define functions to read, add, delete database data

'''

from sqlalchemy import *
from sqlalchemy.orm import *
from sqlalchemy.ext.declarative import declarative_base


# Read data from OpenStack database
def read_from_DB(connection, table_name, obj):
    
    engine = create_engine(connection, echo = False)
    
    metadata = MetaData(engine)
    read_table = Table(table_name, metadata, autoload = True)
    mapper(obj, read_table)
    
    DBSession = sessionmaker(bind = engine)
    R_session = DBSession()

    res = R_session.query(obj).all()
    R_session.close()

    return res


# Input a obejct and return all rows of the obejct from local agent database
def read_all_from_DB(connection, obj):

    engine = create_engine(connection, echo = False)
    
    DBSession = sessionmaker(bind = engine)
    session = DBSession()

    res = session.query(obj).all()
    session.close()

    return res


# Query data from local agent database
def query_from_DB(connection, obj, column, keyword):
    
    engine = create_engine(connection, echo = False)
    
    DBSession = sessionmaker(bind = engine)
    session = DBSession()

    res = session.query(obj).filter(column == keyword)
    session.close()

    return res


# Add data to local agent database
def add_to_DB(connection, obj):
    
    engine = create_engine(connection, echo = False)
    
    # Write to network table of agent DB 
    # Create session of network table of agent DB
    DBSession = sessionmaker(bind = engine)
    session = DBSession()
            
    # Add instance to session
    session.add(obj)

    # Commit session
    session_commit(session)
    session.close()

    
# Delete data from local agent database
def delete_from_DB(connection, obj, column, keyword):
    
    engine = create_engine(connection, echo = False)
    
    DBSession = sessionmaker(bind = engine)
    session = DBSession()

    session.query(obj).filter(column == keyword).delete()
    session.commit()
    session.close()


# A function to commit session
def session_commit(session):
    try:
        # Commit session    
        session.commit()
    except sqlalchemy.exc.IntegrityError, exc:
        reason = exc.message
        session.rollback()
        #if reason.endswith('is not unique'):
        #    print "%s already exists" % exc.params[0]
        #    session.rollback()
    finally:
        # Close session
        session.close()


