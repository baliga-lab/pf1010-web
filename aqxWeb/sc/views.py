from flask import Blueprint, request, session, redirect, url_for, render_template, flash, Response, jsonify,json
from models import User, get_all_recent_posts, get_all_recent_comments
from models import System
from models import get_app_instance, getGraphConnectionURI

from app.scAPI import ScAPI
from flask_login import login_required
from flask_googlelogin import LoginManager, make_secure_token,GoogleLogin
import mysql.connector
import requests
import aqxdb
import logging
import json
from flask_oauth import OAuth
oauth = OAuth()
#GOOGLE_CLIENT_ID='757190606234-pnqru7tabom1p1hhvpm0d3c3lnjk2vv4.apps.googleusercontent.com',
#GOOGLE_CLIENT_SECRET='wklqAsOoVtn44AP-EIePEGmQ',

google = oauth.remote_app('google',
                          base_url='https://www.google.com/accounts/',
                          authorize_url='https://accounts.google.com/o/oauth2/auth',
                          request_token_url=None,
                          request_token_params={'scope': 'https://www.googleapis.com/auth/userinfo.email https://www.googleapis.com/auth/plus.login',
                                                'response_type': 'code'},
                          access_token_url='https://accounts.google.com/o/oauth2/token',
                          access_token_method='POST',
                          access_token_params={'grant_type': 'authorization_code'},
                          consumer_key='757190606234-pnqru7tabom1p1hhvpm0d3c3lnjk2vv4.apps.googleusercontent.com',
                          consumer_secret='wklqAsOoVtn44AP-EIePEGmQ')



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

@social.route('/getToken')
def getToken():
    callback=url_for('social.authorized', _external=True)
    return google.authorize(callback=callback)


@social.route('/oauth2callback')
@google.authorized_handler
def authorized(resp):
    access_token = resp['access_token']
    print(access_token)
    session['access_token'] = access_token, ''
    session['token']=access_token
    return redirect(url_for('social.Home'))


@google.tokengetter
def get_access_token():
    return session.get('access_token')

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
    access_token = session.get('access_token')
    if access_token is None:
        return redirect(url_for('social.getToken'))

    access_token = access_token[0]
    from urllib2 import Request, urlopen, URLError

    headers = {'Authorization': 'OAuth '+access_token}
    req = Request('https://www.googleapis.com/oauth2/v1/userinfo',
                  None, headers)
    try:
        res = urlopen(req)
    except URLError, e:
        if e.code == 401:
            # Unauthorized - bad token
            session.pop('access_token', None)
            return redirect(url_for('social.getToken'))
    return redirect(url_for('social.signin'))



@social.route('/signin')
#######################################################################################
# function : signin
# purpose : signs in with POST and takes data from the request
# parameters : None
# returns: response
# Exception : app.logger.exception
#######################################################################################
def signin():

   try:
        access_token = session.get('access_token')
        access_token = access_token[0]
        r = requests.get('https://www.googleapis.com/plus/v1/people/me?access_token=' + access_token)
       # content=r.content
        print(r.content)
        googleAPIResponse = json.loads(r.content)
        #googleAPIResponsev=json.loads(googleAPIResponse)
        print(googleAPIResponse)
        logging.debug("signed in: %s", str(googleAPIResponse))
        google_id = googleAPIResponse['id']
        if 'image' in googleAPIResponse:
            image=googleAPIResponse['image']
            imgurl = image['url']
        else:
            imgurl = "/static/images/default_profile.png"
        user_id = get_user(google_id, googleAPIResponse)
        emails = googleAPIResponse['emails']
        email = emails[0]['value']
        logging.debug("user: %s img: %s", user_id, imgurl)
        return redirect(url_for('social.index'))
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
# purpose : renders profile_edit.html
# parameters : None
# returns: profile_edit.html
# Exception : None
#######################################################################################
def editprofile():
    if session.get('uid') is not None:
        user = User(session['uid']).find()
        print user
        return render_template("profile_edit.html", user=user)
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
    givenName = request.form.get('givenName', None)
    familyName = request.form.get('familyName', None)
    displayName = request.form.get('displayName', None)
    gender = request.form.get('gender', None)
    print "gender is"
    print gender
    organization = request.form.get('organization', None)
    user_type = request.form.get('user_type', None)
    dateofbirth = request.form.get('dob', None)
    User(session['uid']).updateprofile(givenName, familyName, displayName, gender, organization, user_type, dateofbirth)
    session['displayName'] = displayName
    flash("User Profile Updated successfully!")
    return editprofile()


#######################################################################################
# function : profile
# purpose :
#           google_id : google id fetched from neo4j
# parameters : user_id
# returns: None
# Exception : ?
#######################################################################################
@social.route('/profile/<google_id>', methods=['GET', 'POST'])
def profile(google_id):
    try:
        user_profile = User(session['uid']).get_user_by_google_id(google_id)
        # Invalid User ID
        if user_profile is None:
            return redirect(url_for('social.home'))
        else:
            print user_profile
            return render_template("profile.html", user_profile=user_profile)
    except Exception as e:
        logging.exception("Exception at view_profile: " + str(e))


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


@social.route('/pendingRequest', methods=['GET', 'POST'])
#######################################################################################
# function : pendingRequest
# purpose : renders pendingRequests
# parameters : None
# returns: pendingRequest.html
# Exception : None
#######################################################################################
def pendingRequest():
    if request.method == 'GET':
        if session.get('uid') is not None:
            u_sql_id = User(session['uid']).get_user_sql_id()
            print("sqlid")
            print (u_sql_id)
            pendingRequests = User(session['uid']).get_pending_friend_request(u_sql_id);
            return render_template("/pendingRequest.html",pendingRequests = pendingRequests)
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

@social.route('/send_friend_request/<u_sql_id>', methods=['POST'])
#######################################################################################
# function : send_friend_request
# purpose : send a friend request to a user clicked on the UI
# parameters : None
# returns: calls index function
# Exception : None
#######################################################################################
def send_friend_request(u_sql_id):
    receiver_sql_id = u_sql_id
    User(session['uid']).send_friend_request(receiver_sql_id)
    return redirect(url_for('social.friends'))

#######################################################################################
# function : search_systems
# purpose : renders system_search.html
# parameters : None
# returns: system_search.html
# Exception : None
#######################################################################################
@social.route('/systems', methods=['GET', 'POST'])
@social.route('/systems/', methods=['GET', 'POST'])
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
            return render_template("system_search.html", post_method="true", search_param=systemName,
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
            return render_template("system_search.html", admin_systems=admin_systems,
                                   participated_systems=participated_systems, subscribed_systems=subscribed_systems,
                                   recommended_systems=recommended_systems, all_systems=all_systems)
        else:
            return redirect(url_for('social.index'))

#######################################################################################
# function : view_system
# purpose : renders system_social.html
# parameters : system_uid
# returns: system_social.html
# Exception : General Exception
#######################################################################################

@social.route('/systems/<system_uid>', methods=['GET', 'POST'])
def view_system(system_uid):
    try:
        if request.method == 'GET':
            system_neo4j = System().get_system_by_uid(system_uid)
            # Invalid System_UID
            if system_neo4j is None:
                return redirect(url_for('social.search_systems'))
            else:
                # system_mysql = System().get_mysql_system_by_uid(system_uid)
                system_mysql = system_neo4j
                system_admins = System().get_system_admins(system_uid)
                system_participants = System().get_system_participants(system_uid)
                system_subscribers = System().get_system_subscribers(system_uid)
                participants_pending_approval = System().get_participants_pending_approval(system_uid)
                subscribers_pending_approval = System().get_subscribers_pending_approval(system_uid)
                return render_template("system_social.html", system_neo4j=system_neo4j, system_mysql=system_mysql,
                                       system_admins=system_admins, system_participants=system_participants,
                                       system_subscribers=system_subscribers,
                                       participants_pending_approval=participants_pending_approval,
                                       subscribers_pending_approval=subscribers_pending_approval)
    except Exception as e:
        logging.exception("Exception at view_system: " + str(e))



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
    if comment == "" or comment == None:
        flash('Comment can not be empty')
        redirect(url_for('social.index'))
    elif postid == "" or postid == None:
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
    elif commentid == "" or commentid == None:
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
    elif postid == "" or postid == None:
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

    if commentid == "" or commentid == None:
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
# purpose : used in search friends to return a node in case a match is obtained corresponding
#           to the name that the logged in user has typed
# parameters : None
# returns: json data of existing user's name, organization and friend status
#######################################################################################
@social.route('/getfriends', methods=['GET'])
def getfriends():
    users = User(session['uid']).get_search_friends()
    user_list = []
    sentreq_res, frnds_res = User(session['uid']).get_friends_and_sentreq()

    for result in users:
        individual_user = {}
        first_name = result[0]
        last_name = result[1]
        org = result[2]
        user_sql_id = result[3]
        email = result[4]
        friend_status = "Add Friend"
        for sf in sentreq_res:
            sf_id = sf[0]
            if (user_sql_id == sf_id):
                friend_status = "Sent Friend Request"
        for fr in frnds_res:
            fr_id = fr[0]
            if (user_sql_id == fr_id):
                friend_status = "Friends"

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
        individual_user['friend_status'] = friend_status
        individual_user['user_sql_id'] = user_sql_id
        if email:
            individual_user['email'] = email
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
# API call to put user node in the Neo4J database
######################################################################
@social.route('/aqxapi/put/user', methods=['POST'])
def create_user():
    jsonObject = request.get_json()
    return ScAPI(getGraphConnectionURI()).create_user(jsonObject)


######################################################################
# API call to delete user node in the Neo4J database
######################################################################
@social.route('/aqxapi/delete/user/<sql_id>', methods=['DELETE'])
def delete_user_by_sql_id(sql_id):
    if session.get('siteadmin') is not None:
        return ScAPI(getGraphConnectionURI()).delete_user_by_sql_id(sql_id)


######################################################################
# API call to create system node in the Neo4J database
######################################################################
@social.route('/aqxapi/put/system', methods=['POST'])
def create_system():
    jsonObject = request.get_json()
    return ScAPI(getGraphConnectionURI()).create_system(jsonObject)


######################################################################
# API call to delete system node in the Neo4J database
######################################################################
@social.route('/aqxapi/delete/system/<system_id>', methods=['DELETE'])
def delete_system_by_system_id(system_id):
    if session.get('siteadmin') is not None:
        return ScAPI(getGraphConnectionURI()).delete_system_by_system_id(system_id)
