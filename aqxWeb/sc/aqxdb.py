#The access to the MySQL & Neo4J database is done from here

from flask import session
from datetime import datetime
from py2neo import Node
from models import get_graph_connection_uri, timestamp, User, update_profile_image_url
import uuid

def get_or_create_user(conn, cursor, google_id, googleAPIResponse):

    name = googleAPIResponse.get('name', None)
    if 'image' in googleAPIResponse:
        image=googleAPIResponse['image']
        url = image.get('url', None)
        if url is None:
            imgurl = None
        else:
            #https://lh3.googleusercontent.com/-2jp5fJmzfj4/AAAAAAAAAAI/AAAAAAAAESs/ULgi0QWqsaQ/photo.jpg?sz=200
            indexVal =  url.find("?sz")
            if indexVal != -1:
                imgurl = url[0:indexVal]
            else:
                imgurl = url
    else:
        imgurl = None
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
        user = Node("User", sql_id=result, google_id=google_id, email=email, givenName=givenName, familyName=familyName, displayName=displayName, user_type="subscriber", organization=organization, creation_time=timestamp(), modified_time=timestamp(), dob="", gender=gender, status=0, image_url=imgurl)
        get_graph_connection_uri().create(user)
    else:
        result = row[0]
        user = User(result).find()
        print(user)
        # There might be cases where the Neo4J does not have the corressponding User node
        if user is None:
            missing_user_neo4j = Node("User", sql_id=result, google_id=google_id, email=email, givenName=givenName, familyName=familyName, displayName=displayName, user_type="subscriber", organization=organization, creation_time=timestamp(), modified_time=timestamp(), dob="", gender=gender,image_url=imgurl, status=0)
            get_graph_connection_uri().create(missing_user_neo4j)
        else:
            displayName = user['displayName']
    session['uid']=result
    session['email'] = email
    session['img']=imgurl

    # During Login, The Image Url Is Updated In Neo4J DB To Avoid The Image Discrepancies From Google Account
    if imgurl is not None:
        update_profile_image_url(result, imgurl)

    if displayName is None:
        displayName = ""
    session['displayName'] = displayName
    return result