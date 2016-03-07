from flask import Blueprint, request, session, redirect, url_for, render_template, flash, Response, jsonify
from models import User, get_all_recent_posts, get_all_recent_comments
from models import System
from models import get_app_instance, getGraphConnectionURI
from app.scAPI import ScAPI

import mysql.connector
import requests
import aqxdb
import logging

social = Blueprint('social', __name__, template_folder='templates', static_folder="static")


#######################################################################################
# function : dbconn
# purpose : Connect with DB
# parameters : None
# returns: DB connection
#######################################################################################
def dbconn():
    return mysql.connector.connect(user=get_app_instance().config['USER'],
                                   password=get_app_instance().config['PASS'],
                                   host=get_app_instance().config['HOST'],
                                   database=get_app_instance().config['DB'])


@social.route('/')
@social.route('/index')
#######################################################################################
# function : index
# purpose : renders home page with populated posts and comments
# parameters : None
# returns: home.html, posts and comments
#######################################################################################
def index():
    posts = get_all_recent_posts()
    comments = get_all_recent_comments()
    return render_template('home.html', posts=posts, comments=comments)


@social.route('/login')
#######################################################################################
# function : login
# purpose : renders login.html
# parameters : None
# returns: login.html page
#######################################################################################
def login():
    return render_template('login.html')


@social.route('/Home')
#######################################################################################
# function : home
# purpose : renders userData.html
# parameters : None
# returns: userData.html page
#######################################################################################
def Home():
    return render_template('userData.html')


@social.route('/signin', methods=['POST'])
#######################################################################################
# function : signin
# purpose : signs in with POST and takes data from the request
# parameters : None
# returns: response
# Exception : app.logger.exception
#######################################################################################
def signin():
    try:
        access_token = request.form['access_token']
        print(access_token)
        r = requests.get('https://www.googleapis.com/plus/v1/people/me?access_token=' + access_token)
        googleAPIResponse = r.json()
        # print(googleAPIResponse)
        logging.debug("signed in: %s", str(googleAPIResponse))
        google_id = googleAPIResponse['id']
        if 'picture' in googleAPIResponse:
            imgurl = googleAPIResponse['picture']
        else:
            imgurl = "/static/images/default_profile.png"
        user_id = get_user(google_id, googleAPIResponse)
        emails = googleAPIResponse['emails']
        email = emails[0]['value']
        logging.debug("user: %s img: %s", user_id, imgurl)
        return Response("ok", mimetype='text/plain')
    except:
        logging.exception("Got an exception")
        raise


#######################################################################################
# function : get_user
# purpose :
#           google_id : google id fetched from google+ login
#           googleAPIResponse : JSON response from the google API
# parameters : None
# returns: returns userId
# Exception : ?
#######################################################################################
def get_user(google_id, googleAPIResponse):
    conn = dbconn()
    cursor = conn.cursor()
    try:
        userId = aqxdb.get_or_create_user(conn, cursor, google_id, googleAPIResponse)
        return userId
    finally:
        conn.close()
    print(userID);


@social.route('/editprofile')
#######################################################################################
# function : editprofile
# purpose : renders editProfile.html
# parameters : None
# returns: editProfile.html
# Exception : None
#######################################################################################
def editprofile():
    if session.get('uid') is not None:
        user = User(session['uid']).find()
        return render_template("editProfile.html", user=user)
    else:
        return render_template("/home.html")


#######################################################################################
# function : updateprofile
# purpose : updates user profile information in db
# parameters : None
# returns: None
# Exception : None
#######################################################################################
@social.route('/updateprofile', methods=['POST'])
def updateprofile():
    displayName = request.form['displayName']
    gender = request.form['gender']
    organization = request.form['organization']
    user_type = request.form['user_type']
    dateofbirth = request.form['dob']
    User(session['uid']).updateprofile(displayName, gender, organization, user_type, dateofbirth)
    session['displayName'] = displayName
    flash("User Profile updated successfully")
    return editprofile()


@social.route('/friends', methods=['GET'])
#######################################################################################
# function : friends
# purpose : renders friends.html
# parameters : None
# returns: friends.html
# Exception : None
#######################################################################################
def friends():
    if session.get('uid') is not None:
        return render_template("friends.html")
    else:
        return render_template("/home.html")


@social.route('/pendingRequest', methods=['GET'])
#######################################################################################
# function : pendingRequest
# purpose : renders pendingRequests
# parameters : None
# returns: pendingRequest.html
# Exception : None
#######################################################################################
def pendingRequest():
    if session.get('uid') is not None:
        return render_template("pendingRequest.html")
    else:
        return render_template("/home.html")


@social.route('/searchFriends', methods=['GET'])
#######################################################################################
# function : searchFriends
# purpose : renders searchFriends
# parameters : None
# returns: searchFriends.html
# Exception : None
#######################################################################################
def searchFriends():
    if session.get('uid') is not None:
        return render_template("searchFriends.html")
    else:
        return render_template("/home.html")


#######################################################################################
# function : search_systems
# purpose : renders search_systems.html
# parameters : None
# returns: search_systems.html
# Exception : None
#######################################################################################
@social.route('/systems', methods=['GET', 'POST'])
def search_systems():
    if request.method == 'POST':
        if session.get('uid') is not None:
            systemName = request.form['txtSystemName']
            system_search_results = System().get_system_by_name(systemName)
            admin_systems = System().get_admin_systems(session.get('uid'))
            participated_systems = System().get_participated_systems(session.get('uid'))
            subscribed_systems = System().get_subscribed_systems(session.get('uid'))
            recommended_systems = System().get_recommended_systems(session.get('uid'))
            all_systems = System().get_all_systems()
            return render_template("search_systems.html", post_method="true", search_param=systemName,
                                   system_search_results=system_search_results, admin_systems=admin_systems,
                                   participated_systems=participated_systems, subscribed_systems=subscribed_systems,
                                   recommended_systems=recommended_systems, all_systems=all_systems)
        else:
            return redirect(url_for('social.index'))
    elif request.method == 'GET':
        if session.get('uid') is not None:
            admin_systems = System().get_admin_systems(session.get('uid'))
            participated_systems = System().get_participated_systems(session.get('uid'))
            subscribed_systems = System().get_subscribed_systems(session.get('uid'))
            recommended_systems = System().get_recommended_systems(session.get('uid'))
            all_systems = System().get_all_systems()
            return render_template("search_systems.html", admin_systems=admin_systems,
                                   participated_systems=participated_systems, subscribed_systems=subscribed_systems,
                                   recommended_systems=recommended_systems, all_systems=all_systems)
        else:
            return redirect(url_for('social.index'))


#######################################################################################
# function : view_system
# purpose : renders view_system.html
# parameters : None
# returns: view_system.html
# Exception : None
#######################################################################################
@social.route('/systems/<system_uid>', methods=['GET'])
def view_system(system_uid):
    return "Systems Page Under Construction: " + system_uid

@social.route('/add_comment', methods=['POST'])
#######################################################################################
# function : add_comment
# purpose : adds comments to the post
# parameters : None
# returns: calls index function
# Exception : None
#######################################################################################
def add_comment():
    comment = request.form['newcomment']
    postid = request.form['postid']
    if comment == "" or comment == None :
        flash('Comment can not be empty')
        redirect(url_for('social.index'))
    elif postid == "" or postid == None :
        flash('Post not found to comment on')
        redirect(url_for('social.index'))
    else:
        User(session['uid']).add_comment(comment, postid)
        flash('Your comment has been posted')
    return redirect(url_for('social.index'))

@social.route('/edit_comment', methods=['POST'])
#######################################################################################
# function : edit_comment
# purpose : edits existing comments using unique comment id
# parameters : None
# returns: calls index function
# Exception : None
#######################################################################################
def edit_comment():
    comment = request.form['editedcomment']
    commentid = request.form['commentid']

    if comment == "" or comment == None:
        flash('Comment can not be empty')
        redirect(url_for('social.index'))
    elif commentid == "" or commentid == None :
        flash('Comment not found to edit')
        redirect(url_for('social.index'))
    else:
        User(session['uid']).edit_comment(comment, commentid)
        flash('Your comment has been updated')
    return redirect(url_for('social.index'))


@social.route('/edit_post', methods=['POST'])
#######################################################################################
# function : edit_post
# purpose : edits existing comments using unique comment id
# parameters : None
# returns: calls index function
# Exception : None
#######################################################################################
def edit_post():
    newpost = request.form['editedpost']
    postid = request.form['postid']

    if newpost == "" or newpost == None:
        flash('New post can not be empty')
        redirect(url_for('social.index'))
    elif postid == "" or postid == None :
        flash('Post not found to edit')
        redirect(url_for('social.index'))
    else:
        User(session['uid']).edit_post(newpost, postid)
        flash('Your comment has been updated')
    return redirect(url_for('social.index'))


@social.route('/delete_comment', methods=['POST'])
#######################################################################################
# function : delete_comment
# purpose : edits existing comments using unique comment id
# parameters : None
# returns: calls index function
# Exception : None
#######################################################################################
def delete_comment():
    commentid = request.form['commentid']

    if commentid == "" or commentid == None :
        flash('Comment not found to delete')
        redirect(url_for('social.index'))
    else:
        User(session['uid']).delete_comment(commentid)
        flash('Your comment has been updated')
    return redirect(url_for('social.index'))

@social.route('/add_post', methods=['POST'])
#######################################################################################
# function : add_post
# purpose : adds posts newly created by user
# parameters : None
# returns: calls index function
# Exception : None
#######################################################################################
def add_post():
    if session.get('uid') is not None:
        privacy = request.form['privacy']
        text = request.form['text']
        link = request.form['link']
        if text == "":
            flash('Post cannot be empty.')
        else:
            User(session['uid']).add_post(text, privacy, link)
            flash('Your post has been shared')
    return redirect(url_for('social.index'))

@social.route('/delete_post', methods=['POST'])
#######################################################################################
# function : delete_post
# purpose : removes post and it's related realtionships and comments
# parameters : None
# returns: calls index function
# Exception : None
#######################################################################################
def delete_post():
    if session.get('uid') is not None:
        postid = request.form['postid']
        if postid == "":
            flash('Can not find the post to delete.')
        else:
            User(session['uid']).delete_post(postid)
            flash('Your post has been deleted')
    return redirect(url_for('social.index'))

@social.route('/like_post', methods=['POST'])
#######################################################################################
# function : like_post
# purpose : like posts previously created by user
# parameters : None
# returns: calls index function
# Exception : None
#######################################################################################
def like_post():
    if session.get('uid') is not None:
        postid = request.form['postid']
        User(session['uid']).like_post(postid)
        flash('You liked the post')
        return redirect(url_for('social.index'))
    else:
        return render_template("/home.html")

@social.route('/unlike_post', methods=['POST'])
#######################################################################################
# function : unlike_post
# purpose : unlike post previously liked by user
# parameters : None
# returns: calls index function
# Exception : None
#######################################################################################
def unlike_post():
    if session.get('uid') is not None:
        postid = request.form['postid']
        User(session['uid']).unlike_post(postid)
        flash('You unliked the post')
        return redirect(url_for('social.index'))
    else:
        return render_template("/home.html")
#######################################################################################
# function : getfriends
# purpose : used in search friends to return a node in case a match is obtained
# parameters : None
# returns: json data of existing user names
#######################################################################################
@social.route('/getfriends',methods=['GET'])
def getfriends():
    users = User(session['uid']).get_search_friends()
    user_list = []
    for result in users:
        individual_user = {}
        first_name = result[0]
        last_name = result[1]
        org = result[2]
        if not first_name and not last_name:
            full_name = None
        elif not first_name:
            full_name = last_name
        elif not last_name:
            full_name = first_name
        else:
            full_name = first_name + " " + last_name
        if full_name:
            individual_user['label'] = full_name
        if org:
            individual_user['org'] = org
        if individual_user:
            user_list.append(individual_user)
    print user_list

    return jsonify(json_list=user_list)

@social.route('/logout')
#######################################################################################
# function : logout
# purpose : logout of current session
# parameters : None
# returns: calls index function
# Exception : None
#######################################################################################
def logout():
    session.pop('uid', None)
    session.pop('email', None)
    session.pop('displayName', None)
    flash('Logged out.')
    return redirect(url_for('index'))


@social.route('/testSignin', methods=['POST'])
#######################################################################################
# function : Test Insertion and deletion of the user in Neo4j and mySql
# purpose : signs in with POST and takes data from the request
# parameters : None
# returns: response
# Exception : app.logger.exception
#######################################################################################
def testSignin():
    try:
        GivenName = request.form['givenName']
        familyName = request.form['familyName']
        email = request.form['email']
        user_id = request.form['id']
        user_id = get_user(user_id, email, GivenName, familyName)
        return Response("ok", mimetype='text/plain')
    except:
        logging.exception("Got an exception")
        raise


######################################################################
# API call to get logged in user data
######################################################################
@social.route('/aqxapi/get/user/logged_in_user/', methods=['GET'])
def get_logged_in_user():
    return ScAPI(getGraphConnectionURI()).get_logged_in_user()



######################################################################
# API call to get user data for the specified google_id
######################################################################
@social.route('/aqxapi/get/user/by_google_id/<google_id>', methods=['GET'])
def get_user_by_google_id(google_id):
    return ScAPI(getGraphConnectionURI()).get_user_by_google_id(google_id)


######################################################################
# API call to get user data for the specified sql_id
######################################################################
@social.route('/aqxapi/get/user/by_sql_id/<sql_id>', methods=['GET'])
def get_user_by_sql_id(sql_id):
    return ScAPI(getGraphConnectionURI()).get_user_by_sql_id(sql_id)

######################################################################
# API call to put user data
######################################################################
@social.route('/aqxapi/put/user', methods=['POST'])
def create_user():
    jsonObject = request.get_json()
    return ScAPI(getGraphConnectionURI()).create_user(jsonObject)

######################################################################
# API call to put user data
######################################################################
@social.route('/aqxapi/delete/user/<sql_id>', methods=['DELETE'])
def delete_user_by_sql_id(sql_id):
    if session.get('siteadmin') is not None:
        return ScAPI(getGraphConnectionURI()).delete_user_by_sql_id(sql_id)

