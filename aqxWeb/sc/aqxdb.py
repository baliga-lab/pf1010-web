#The access to the MySQL & Neo4J database is done from here

from flask import session
from datetime import datetime
from py2neo import Node
from models import getGraphConnectionURI, timestamp, User
import uuid

def get_or_create_user(conn, cursor, google_id, googleAPIResponse):
    name = googleAPIResponse.get('name', None)
    if name is None:
        givenName = None
        displayName = None
        familyName = None
    else:
        givenName = name.get('givenName', None)
        displayName = givenName
        familyName = name.get('familyName', None)
    emails = googleAPIResponse.get('emails', None)
    if emails is None:
        email = None
    else:
        email = emails[0]['value']
    gender = googleAPIResponse.get('gender', None)
    organizations = googleAPIResponse.get('organizations', None)
    if organizations is None:
        organization = None
    else:
        organization = organizations[0]['name']
    cursor.execute('select id from users where google_id=%s', [google_id])
    row = cursor.fetchone()
    if row is None:
        # create user
        cursor.execute('insert into users (google_id, email) values (%s,%s)', [google_id, email])
        result = cursor.lastrowid
        conn.commit()
        user = Node("User", sql_id=result, google_id=google_id, email=email, givenName=givenName, familyName=familyName, displayName=displayName, user_type="subscriber", organization=organization, creation_time=timestamp(), modified_time=timestamp(), dob="", gender=gender, status=0)
        getGraphConnectionURI().create(user)
    else:
        result = row[0]
        user = User(result).find()
        # There might be cases where the Neo4J does not have the corressponding User node
        if user is None:
            missing_user_neo4j = Node("User", sql_id=result, google_id=google_id, email=email, givenName=givenName, familyName=familyName, displayName=displayName, user_type="subscriber", organization=organization, creation_time=timestamp(), modified_time=timestamp(), dob="", gender=gender, status=0)
            getGraphConnectionURI().create(missing_user_neo4j)
        else:
            displayName = user['displayName']
    session['uid']=result
    session['email'] = email
    if displayName is None:
        displayName = ""
    session['displayName'] = displayName
    return result