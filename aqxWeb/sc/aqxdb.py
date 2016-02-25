#The access to the MySQL & Neo4J database is done from here

from flask import current_app, session
from datetime import datetime
from py2neo import Node
from models import graph, timestamp, User
import uuid

def get_or_create_user(conn, cursor, google_id, googleAPIResponse):
    name = googleAPIResponse['name']
    givenName = name['givenName']
    displayName = givenName
    familyName = name['familyName']
    emails = googleAPIResponse['emails']
    email = emails[0]['value']
    gender = googleAPIResponse['gender']
    organizations = googleAPIResponse['organizations']
    organization = organizations[0]['name']
    cursor.execute('select id from users where google_id=%s', [google_id])
    row = cursor.fetchone()
    if row is None:
        # create user
        cursor.execute('insert into users (google_id, email) values (%s,%s)', [google_id, email])
        result = cursor.lastrowid
        conn.commit()
        user = Node("User", sql_id=result, google_id=google_id, email=email, givenName=givenName, familyName=familyName, displayName=displayName, user_type="Subscriber", organization=organization, creation_time=timestamp(), modified_time=timestamp(), dob="", gender=gender, status=0)
        graph.create(user)
    else:
        result = row[0]
        displayName = User(result).find()['displayName']
        #insertIntoNeo(neoDb,google_id,email,result,GivenName,familyName)
    session['uid']=result
    session['email'] = email
    session['displayName'] = displayName
    return result

'''
def insertIntoNeo(neoDb,google_id,email,result,GivenName,familyName):
    Users = neoDb.labels.create("Users")
    print(google_id)	
    u1 = neoDb.nodes.create(email=email,status="1",user_type="Subscriber",name=GivenName,modified_time="1455466583873",dob="1455466583873",creation_time="1455466583873",google_id=google_id,gender="male",sql_id=result)
    Users.add(u1)'''
	
 
	