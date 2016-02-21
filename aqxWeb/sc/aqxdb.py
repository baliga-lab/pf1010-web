#The access to the main database is done from here

from flask import current_app
from datetime import datetime
from py2neo import Node
from models import graph
import uuid

def get_or_create_user(conn, cursor, google_id, email,GivenName,familyName):
    cursor.execute('select id from users where google_id=%s', [google_id])
    row = cursor.fetchone()
    if row is None:
        # create user
        cursor.execute('insert into users (google_id, email) values (%s,%s)', [google_id, email])
        result = cursor.lastrowid
        conn.commit()
        user = Node("User",email=email,status="1",user_type="Subscriber",username=GivenName,name=GivenName,modified_time="1455466583873",dob="1455466583873",creation_time="1455466583873",google_id=google_id,gender="male",sql_id=result )
        graph.create(user)
    else:
        result = row[0]
        #insertIntoNeo(neoDb,google_id,email,result,GivenName,familyName)
    return result

'''
def insertIntoNeo(neoDb,google_id,email,result,GivenName,familyName):
    Users = neoDb.labels.create("Users")
    print(google_id)	
    u1 = neoDb.nodes.create(email=email,status="1",user_type="Subscriber",name=GivenName,modified_time="1455466583873",dob="1455466583873",creation_time="1455466583873",google_id=google_id,gender="male",sql_id=result)
    Users.add(u1)'''
	
 
	