from flask import Blueprint, request, session, redirect, url_for, render_template, flash, Response, jsonify, json
from models import User, get_all_recent_posts, get_all_recent_comments, get_all_recent_likes
from models import get_total_likes_for_posts, get_all_post_owners
from models import System, Privacy
from models import get_app_instance, getGraphConnectionURI
from models import get_all_profile_posts
from py2neo import cypher
from app.scAPI import ScAPI
from flask_login import login_required
from flask_googlelogin import LoginManager, make_secure_token, GoogleLogin
from models import convert_milliseconds_to_normal_date, get_sql_id, get_address_from_lat_lng
import mysql.connector
import requests
import aqxdb
import logging
import json
from flask_oauth import OAuth

oauth = OAuth()
# GOOGLE_CLIENT_ID='757190606234-pnqru7tabom1p1hhvpm0d3c3lnjk2vv4.apps.googleusercontent.com',
# GOOGLE_CLIENT_SECRET='wklqAsOoVtn44AP-EIePEGmQ',

google = oauth.remote_app('google',
                          base_url='https://www.google.com/accounts/',
                          authorize_url='https://accounts.google.com/o/oauth2/auth',
                          request_token_url=None,
                          request_token_params={
                              'scope': 'https://www.googleapis.com/auth/userinfo.email https://www.googleapis.com/auth/plus.login',
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
    callback = url_for('social.authorized', _external=True)
    return google.authorize(callback=callback)


@social.route('/oauth2callback')
@google.authorized_handler
def authorized(resp):
    access_token = resp['access_token']
    # print(access_token)
    session['access_token'] = access_token, ''
    session['token'] = access_token
    return redirect(url_for('social.Home'))


@google.tokengetter
def get_access_token():
    return session.get('access_token')


@social.route('/trial')
def trial():
    return render_template('dummy.html')


@social.route('/index')
#######################################################################################
# function : index
# purpose : renders home page with populated posts and comments
# parameters : None
# returns: home.html, posts and comments
#######################################################################################
def index():
    if session.get('uid') is None:
        return redirect(url_for('index'))  # if no session, return to login
    posts = get_all_recent_posts(session.get('uid'))
    comments = get_all_recent_comments()
    likes = get_all_recent_likes()
    totalLikes = get_total_likes_for_posts()
    postOwners = get_all_post_owners()
    privacy = Privacy([Privacy.FRIENDS, Privacy.PUBLIC], Privacy.FRIENDS,
                      'home', session['uid'])  # info about timeline/page)
    privacy.user_relation = None
    return render_template('home.html', posts=posts, comments=comments,
                           privacy_info=privacy, likes=likes,
                           totalLikes=totalLikes, postOwners=postOwners)


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

    headers = {'Authorization': 'OAuth ' + access_token}
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
        # print(r.content)
        googleAPIResponse = json.loads(r.content)
        # googleAPIResponsev=json.loads(googleAPIResponse)
        # print(googleAPIResponse)
        logging.debug("signed in: %s", str(googleAPIResponse))
        google_id = googleAPIResponse['id']
        if 'image' in googleAPIResponse:
            image = googleAPIResponse['image']
            imgurl = image['url']
        else:
            imgurl = "/static/images/default_profile.png"
        session['img'] = imgurl
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


#######################################################################################
# function : get_google_profile
# purpose : returns user profile data using Google API
# parameters:
#           google_id : google id for google+ login
# returns: google API response
# Exception : ?
#######################################################################################
def get_google_profile(google_id):
    try:
        access_token = session.get('access_token')
        access_token = access_token[0]
        r = requests.get('https://www.googleapis.com/plus/v1/people/' + google_id + '?access_token=' + access_token)

        google_profile = {
            "google_id": google_id
        }

        google_response = json.loads(r.content)
        if google_response and not google_response.get('error'):
            logging.debug("profile of: %s", str(google_response))

            img_url = None
            google_plus_account_url = google_response.get("url", None)
            plus_url = ""
            # getting image url
            if 'image' in google_response:
                image = google_response['image']
                img_url = image['url'].replace('?sz=50', '')

            if google_plus_account_url is not None:
                plus_url = google_response.get('url')

            google_profile = {
                "google_id": google_id,
                "displayName": google_response.get('displayName'),
                "plus_url": plus_url,
                "img_url": img_url
            }

        return google_profile
    except Exception as e:
        logging.exception("Exception at get_google_profile: " + str(e))


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
        # google_profile = get_google_profile('me')
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
    if session.get('uid') is None:
        return redirect(url_for('social.index'))
    givenName = request.form.get('givenName', None)
    familyName = request.form.get('familyName', None)
    displayName = request.form.get('displayName', None)
    gender = request.form.get('gender', None)
    print "gender is"
    print gender
    organization = request.form.get('organization', None)
    user_type = request.form.get('user_type', None)
    dateofbirth = request.form.get('dob', None)
    User(session['uid']).update_profile(givenName, familyName, displayName, gender, organization, user_type, dateofbirth)
    session['displayName'] = displayName
    flash("User Profile Updated successfully!")
    return editprofile()


#######################################################################################
# function : profile
# purpose : Load the pages for user given its google id
# parameters : google_id : google id fetched from neo4j
# returns: profile.html
# Exception : ?
#######################################################################################
@social.route('/profile/<google_id>', methods=['GET'])
def profile(google_id):
    if session.get('uid') is None:
        return redirect(url_for('social.index'))

    try:
        # getting data from neo4j
        if google_id == "me":
            sql_id = session['uid']
            admin_systems = System().get_admin_systems(session['uid'])
            participated_systems = System().get_participated_systems(session['uid'])
            subscribed_systems = System().get_subscribed_systems(session['uid'])
            friends = User(session['uid']).get_my_friends(session['uid']);
            status = "Me"
        else:
            result = get_sql_id(google_id)
            if not (result and result.one):
                return redirect(url_for('social.Home'))
            else:
                sql_id = result.one
                status = checkStatus(sql_id)
                admin_systems = System().get_admin_systems(sql_id)
                participated_systems = System().get_participated_systems(sql_id)
                subscribed_systems = System().get_subscribed_systems(sql_id)
                friends = User(session['uid']).get_my_friends(sql_id)

        # Invalid User
        user_profile = User(sql_id).find()
        if user_profile is None:
            return redirect(url_for('social.home'))
        else:
            # accessing google API to retrieve profile data
            google_profile = get_google_profile(google_id)
            if not (google_profile and google_profile.get('displayName')):
                display_name = user_profile['displayName']
                if not display_name:
                    display_name = user_profile['email']
                    display_name = display_name.split('@', 1)[0]
                google_profile = {
                    "display_name": display_name,
                    "google_id": user_profile['google_id'],
                    "plus_url": "#",
                    "img_url": ""
                }

            privacy_default = Privacy.FRIENDS
            user_relation = Privacy.PUBLIC
            if sql_id == session.get('uid'):
                privacy_options = [Privacy.FRIENDS, Privacy.PUBLIC]
                user_relation = Privacy.PRIVATE  # profile of logged user can access private posts
            else:
                if User(sql_id).is_friend(sql_id, session.get('uid')):
                    privacy_options = [Privacy.FRIENDS, Privacy.PRIVATE, Privacy.PUBLIC]
                    user_relation = Privacy.FRIENDS  # user is friend with profile's user
                else:
                    privacy_options = [Privacy.PRIVATE]
                    privacy_default = Privacy.PRIVATE

            privacy = Privacy(privacy_options, privacy_default, 'profile', sql_id)  # info about timeline/page
            privacy.user_relation = user_relation.lower()

            posts = get_all_profile_posts(sql_id)

            return render_template("profile.html", user_profile=user_profile, google_profile=google_profile,
                                   posts=posts, privacy_info=privacy, participated_systems=participated_systems,
                                   subscribed_systems=subscribed_systems, admin_systems=admin_systems,
                                   friends=friends, status=status, sqlId=sql_id)

    except Exception as e:
        logging.exception("Exception at view_profile: " + str(e))


#######################################################################################
# function : friends
# purpose : renders friends.html to let the user perform activities related to friends
# parameters : None
# returns: friends.html
# Exception : None
###############################################################################
# @social.route('/friends', methods=['GET'])
# def friends():
#    if session.get('uid') is not None:
#        return render_template("friends.html")
#    else:
#        return render_template("/home.html")

#######################################################################################
# function : accept_friend_request
# purpose : renders friends.html to let the user perform activities related to friends
# parameters : None
# returns: friends.html
# Exception : None
###############################################################################
@social.route('/accept_friend_request/<u_sql_id>', methods=['GET', 'POST'])
def accept_friend_request(u_sql_id):
    accepted_sql_id = u_sql_id
    User(session['uid']).accept_friend_request(accepted_sql_id)
    User(session['uid']).delete_friend_request(accepted_sql_id)
    flash('Friend Request Accepted');
    return redirect(url_for('social.pendingRequest'))


#######################################################################################
# function : decline_friend_request
# purpose : declines friend request
# parameters : None
# returns: pendingRequest.html
# Exception : None
###############################################################################
@social.route('/decline_friend_request/<u_sql_id>', methods=['GET', 'POST'])
def decline_friend_request(u_sql_id):
    accepted_sql_id = u_sql_id
    User(session['uid']).delete_friend_request(accepted_sql_id)
    flash('Friend Request Deleted');
    return redirect(url_for('social.pendingRequest'))


#######################################################################################
# function : block_friend
# purpose : blocks a friend
# parameters : None
# returns: friends.html
# Exception : None
###############################################################################
@social.route('/block_friend/<u_sql_id>', methods=['GET', 'POST'])
def block_friend(u_sql_id):
    blocked_sql_id = u_sql_id
    User(session['uid']).block_a_friend(blocked_sql_id)
    flash('Friend Blocked');
    return redirect(url_for('social.friends'))


#######################################################################################
# function : unblock_friend
# purpose : unblocks a friend
# parameters : None
# returns: friends.html
# Exception : None
###############################################################################
@social.route('/unblock_friend/<u_sql_id>', methods=['GET', 'POST'])
def unblock_friend(u_sql_id):
    blocked_sql_id = u_sql_id
    User(session['uid']).unblock_a_friend(blocked_sql_id)
    flash('Friend Blocked');
    return redirect(url_for('social.friends'))


#######################################################################################
# function : delete_friend
# purpose : deletes friend
# parameters : None
# returns: friends.html
# Exception : None
###############################################################################
@social.route('/delete_friend/<u_sql_id>', methods=['GET', 'POST'])
def delete_friend(u_sql_id):
    accepted_sql_id = u_sql_id
    User(session['uid']).delete_friend(accepted_sql_id)
    flash('Friend  Deleted');
    return redirect(url_for('social.friends'))


#######################################################################################
# function : myFriends
# purpose : renders Friends of the logged in user
# parameters : None
# returns: friends.html
# Exception : None
#######################################################################################
@social.route('/friends', methods=['GET', 'POST'])
def friends():
    if request.method == 'GET':
        if session.get('uid') is not None:
            u_sql_id = User(session['uid']).get_user_sql_id()
            print("sqlid")
            print (u_sql_id)
            Friends = User(session['uid']).get_my_friends(u_sql_id);

            UnblockedFriend = User(session['uid']).get_my_blocked_friends(u_sql_id);
            print("Unblocked")
            print(UnblockedFriend)
            return render_template("/friends.html", Friends=Friends, UnblockedFriend=UnblockedFriend)

            return render_template("/friends.html", Friends=Friends)

    else:
        return render_template("/home.html")


#######################################################################################
# function : pendingRequest
# purpose : renders pendingRequests of the logged in user
# parameters : None
# returns: pendingRequest.html
# Exception : None
#######################################################################################
@social.route('/pendingRequest', methods=['GET', 'POST'])
def pendingRequest():
    if request.method == 'GET':
        if session.get('uid') is not None:
            u_sql_id = User(session['uid']).get_user_sql_id()
            print("sqlid")
            print (u_sql_id)
            pendingRequests = User(session['uid']).get_pending_friend_request(u_sql_id);
            return render_template("/pendingRequest.html", pendingRequests=pendingRequests)
    else:
        return render_template("/home.html")


#######################################################################################
# function : recofriends
# purpose : display the logged in user's recommended friends list
# parameters : None
# returns: recofriends.html in case the user is logged in
#          or home.html in case the user is not logged in
# Exception : None
#######################################################################################
@social.route('/recofriends')
def recofriends():
    if session.get('uid') is not None:
        reco_friends = User(session['uid']).get_recommended_frnds()
        return_list = []
        for row in reco_friends:
            reco_user = {}
            mutual_row = User(session['uid']).get_mutual_friends(row.sid)
            reco_user['r_friend'] = row
            reco_user['m_info'] = mutual_row
            return_list.append(reco_user)
        return render_template("recofriends.html", recolist=return_list)
    else:
        return render_template("/home.html")


#######################################################################################
# function : searchFriends
# purpose : lets the user search for friends and add them if necessary
# parameters : None
# returns: searchFriends.html in case the user is logged in
#          or home.html in case the user is not logged in
# Exception : None
#######################################################################################
@social.route('/searchFriends', methods=['GET'])
def searchFriends():
    if session.get('uid') is not None:
        return render_template("SearchFriends.html")
    else:
        return render_template("/home.html")


#######################################################################################
# function : send_friend_request
# purpose : send a friend request to a user clicked on the UI
# parameters : None
# returns: calls index function
# Exception : None
#######################################################################################
@social.route('/send_friend_request/<u_sql_id>', methods=['GET', 'POST'])
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
    sql_id = session.get('uid')
    # sql_id = 29
    if sql_id is None:
        return redirect(url_for('social.index'))
    else:
        if request.method == 'POST':
            systemName = request.form['txtSystemName']
            system_search_results = System().get_system_by_name(systemName)
            admin_systems = System().get_admin_systems(sql_id)
            participated_systems = System().get_participated_systems(sql_id)
            subscribed_systems = System().get_subscribed_systems(sql_id)
            recommended_systems = System().get_recommended_systems(sql_id)
            all_systems = System().get_all_systems()
            return render_template("system_search.html", post_method="true", search_param=systemName,
                                   system_search_results=system_search_results, admin_systems=admin_systems,
                                   participated_systems=participated_systems, subscribed_systems=subscribed_systems,
                                   recommended_systems=recommended_systems, all_systems=all_systems)
        elif request.method == 'GET':
            admin_systems = System().get_admin_systems(sql_id)
            participated_systems = System().get_participated_systems(sql_id)
            subscribed_systems = System().get_subscribed_systems(sql_id)
            recommended_systems = System().get_recommended_systems(sql_id)
            all_systems = System().get_all_systems()
            return render_template("system_search.html", admin_systems=admin_systems,
                                   participated_systems=participated_systems, subscribed_systems=subscribed_systems,
                                   recommended_systems=recommended_systems, all_systems=all_systems)


#######################################################################################
# function : view_system
# purpose : renders system_social.html
# parameters : system_uid
# returns: system_social.html
# Exception : General Exception
#######################################################################################

@social.route('/systems/<system_uid>', methods=['GET', 'POST'])
def view_system(system_uid):
    sql_id = session.get('uid')
    #sql_id = 29
    #system_uid = "2e79ea8a411011e5aac7000c29b92d09"
    if sql_id is None:
        return redirect(url_for('social.search_systems'))
    try:
        system = System()
        if request.method == 'GET':
            system_neo4j = system.get_system_by_uid(system_uid)
            # InValid System_UID
            if not system_neo4j:
                return redirect(url_for('social.search_systems'))
            # Valid System_UID
            else:
                logged_in_user = User(sql_id).find()
                created_date = convert_milliseconds_to_normal_date(system_neo4j[0][0]['creation_time'])
                system_location = get_address_from_lat_lng(system_neo4j[0][0]['location_lat'],
                                                           system_neo4j[0][0]['location_lng'])
                # system_mysql = System().get_mysql_system_by_uid(system_uid)
                system_mysql = system_neo4j
                # measurements = analyticsViews.get_system_measurements(sql_id)
                # print (measurements)
                user_privilege = system.get_user_privilege_for_system(sql_id, system_uid)
                system_admins = system.get_system_admins(system_uid)
                system_participants = system.get_system_participants(system_uid)
                system_subscribers = system.get_system_subscribers(system_uid)
                participants_pending_approval = system.get_participants_pending_approval(system_uid)
                subscribers_pending_approval = system.get_subscribers_pending_approval(system_uid)
                privacy_options = {"Members", "Public"}
                posts = system.get_system_recent_posts(system_uid)
                comments = system.get_system_recent_comments(system_uid)
                likes = system.get_system_recent_likes(system_uid)
                totalLikes = system.get_total_likes_for_system_posts(system_uid)
                postOwners = system.get_system_post_owners(system_uid)

                return render_template("system_social.html", system_neo4j=system_neo4j, system_mysql=system_mysql,
                                       logged_in_user=logged_in_user, created_date=created_date,
                                       system_location=system_location,
                                       user_privilege=user_privilege, system_admins=system_admins,
                                       system_participants=system_participants, system_subscribers=system_subscribers,
                                       participants_pending_approval=participants_pending_approval,
                                       subscribers_pending_approval=subscribers_pending_approval,
                                       system_uid=system_uid, privacy_options=privacy_options,
                                       posts=posts, comments=comments, likes=likes,
                                       totalLikes=totalLikes, postOwners=postOwners)
    except Exception as e:
        logging.exception("Exception at view_system: " + str(e))


#######################################################################################
@social.route('/systems/approve_reject_participant', methods=['POST'])
# function : approve_reject_participant for a system
# purpose : approve/reject the participant request made for the particular system
# parameters : None
# Exception : None
#######################################################################################
def approve_reject_system_participant():
    if request.method == 'POST':
        system_uid = request.form["system_uid"]
        google_id = request.form["google_id"]
        system = System()
        sql_id = session.get('uid')
        # sql_id = 1;
        if sql_id is not None:
            user_privilege = system.get_user_privilege_for_system(sql_id, system_uid)
            if user_privilege == "SYS_ADMIN":
                if request.form['submit'] == 'Approve':
                    system.approve_system_participant(google_id, system_uid)
                elif request.form['submit'] == 'Reject':
                    system.reject_system_participant(google_id, system_uid)
        return redirect(url_for('social.view_system', system_uid=system_uid))
    else:
        return redirect(url_for('social.search_systems'))


#######################################################################################
@social.route('/systems/participate_subscribe_leave', methods=['POST'])
# function : join_system
# purpose : Subscribe/Request To Join the system by an User for the particular system
# parameters : None
# Exception : None
#######################################################################################
def participate_subscribe_leave_system():
    if request.method == 'POST':
        system_uid = request.form["system_uid"]
        google_id = request.form["google_id"]
        system = System()
        sql_id = session.get('uid')
        # sql_id = 1;
        if sql_id is not None:
            user_privilege = system.get_user_privilege_for_system(sql_id, system_uid)
            if user_privilege is None:
                if request.form['submit'] == 'Subscribe':
                    system.subscribe_to_system(google_id, system_uid)
                elif request.form['submit'] == 'Participate':
                    system.pending_participate_to_system(google_id, system_uid)
            else:
                if user_privilege == "SYS_ADMIN" or user_privilege == "SYS_PARTICIPANT" or user_privilege == "SYS_SUBSCRIBER" \
                        or user_privilege == "SYS_PENDING_PARTICIPANT" or user_privilege == "SYS_PENDING_SUBSCRIBER":
                    if request.form['submit'] == 'Leave':
                        system.leave_system(google_id, system_uid)
        return redirect(url_for('social.view_system', system_uid=system_uid))
    else:
        return redirect(url_for('social.search_systems'))


#######################################################################################
# function : search_systems
# purpose : renders system_search.html
# parameters : None
# returns: system_search.html
# Exception : None
#######################################################################################
@social.route('/manage/systems/<system_uid>', methods=['GET', 'POST'])
def manage_system(system_uid):
    sql_id = session.get('uid')
    # sql_id = 29
    # system_uid = "416f3f2e3fe411e597b1000c29b92e09"
    if sql_id is None:
        return redirect(url_for('social.index'))
    system = System()
    logged_in_user = User(sql_id).find()
    system_neo4j = system.get_system_by_uid(system_uid)
    # InValid System_UID
    if not system_neo4j:
        return redirect(url_for('social.search_systems'))
    user_privilege = system.get_user_privilege_for_system(sql_id, system_uid)
    # Only Admin of The System Has Privileges To Access The Settings Page
    if user_privilege != "SYS_ADMIN":
        return redirect(url_for('social.search_systems'))
    if request.method == 'GET':
        participants_pending_approval = system.get_participants_pending_approval(system_uid)
        system_admins = system.get_system_admins(system_uid)
        system_participants = system.get_system_participants(system_uid)
        system_subscribers = system.get_system_subscribers(system_uid)
        return render_template("system_manage.html", system_neo4j=system_neo4j, logged_in_user=logged_in_user,
                               participants_pending_approval=participants_pending_approval,
                               system_admins=system_admins, system_participants=system_participants,
                               system_subscribers=system_subscribers)
    elif request.method == 'POST':
        return render_template("system_manage.html")


#######################################################################################
@social.route('/manage/systems/delete_system_participant_or_make_admin', methods=['POST'])
# function : delete_or_make_admin_system_participant
# purpose : Delete the participant from the system or make him/her as admin of the system
# parameters : None
# Exception : None
#######################################################################################
def delete_system_participant_or_make_admin():
    if request.method == 'POST':
        system_uid = request.form["system_uid"]
        google_id = request.form["google_id"]
        system = System()
        sql_id = session.get('uid')
        # sql_id = 29;
        if sql_id is not None:
            user_privilege = system.get_user_privilege_for_system(sql_id, system_uid)
            if user_privilege == "SYS_ADMIN":
                if request.form['submit'] == 'DeleteParticipant':
                    system.delete_system_participant(google_id, system_uid)
                elif request.form['submit'] == "MakeAdmin":
                    system.make_admin_for_system(google_id, system_uid)
                elif request.form['submit'] == "MakeSubscriber":
                    system.make_subscriber_for_system(google_id, system_uid)
        return redirect(url_for('social.manage_system', system_uid=system_uid))
    else:
        return redirect(url_for('social.search_systems'))


#######################################################################################
@social.route('/manage/systems/delete_admin', methods=['POST'])
# function : make_or_delete_system_admin
# purpose : Makes the participant admin for the system
# parameters : None
# Exception : None
#######################################################################################
def delete_system_admin():
    if request.method == 'POST':
        system_uid = request.form["system_uid"]
        google_id = request.form["google_id"]
        system = System()
        sql_id = session.get('uid')
        # sql_id = 29;
        if sql_id is not None:
            user_privilege = system.get_user_privilege_for_system(sql_id, system_uid)
            if user_privilege == "SYS_ADMIN":
                if request.form['submit'] == 'DeleteAdmin':
                    system.delete_system_admin(google_id, system_uid)
        return redirect(url_for('social.manage_system', system_uid=system_uid))
    else:
        return redirect(url_for('social.search_systems'))


#######################################################################################
@social.route('/manage/systems/delete_system_subscriber_or_make_admin', methods=['POST'])
# function : delete_system_subscriber_or_make_admin
# purpose : Delete the Subscriber from the System or make him/her as admin of the System
# parameters : None
# Exception : None
#######################################################################################
def delete_system_subscriber_or_make_admin():
    if request.method == 'POST':
        system_uid = request.form["system_uid"]
        google_id = request.form["google_id"]
        system = System()
        sql_id = session.get('uid')
        # sql_id = 29;
        if sql_id is not None:
            user_privilege = system.get_user_privilege_for_system(sql_id, system_uid)
            if user_privilege == "SYS_ADMIN":
                if request.form['submit'] == 'DeleteSubscriber':
                    system.delete_system_subscriber(google_id, system_uid)
                elif request.form['submit'] == "MakeAdmin":
                    system.make_admin_for_system(google_id, system_uid)
                elif request.form['submit'] == "MakeParticipant":
                    system.make_participant_for_system(google_id, system_uid)
        return redirect(url_for('social.manage_system', system_uid=system_uid))
    else:
        return redirect(url_for('social.search_systems'))


#######################################################################################
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
        redirect(request.referrer)
    elif postid == "" or postid == None:
        flash('Post not found to comment on')
        redirect(request.referrer)
    else:
        User(session['uid']).add_comment(comment, postid)
        flash('Your comment has been posted')

    return redirect(request.referrer)


@social.route('/edit_or_delete_comment', methods=['POST'])
#######################################################################################
# function : edit_or_delete_comment
# purpose : edits or delete existing comments using unique comment id
# parameters : None
# returns: calls index function
# Exception : None
#######################################################################################
def edit_or_delete_comment():
    if session.get('uid') is not None:
        commentid = request.form['commentid']
        # system_uid = request.form["system_uid"]
        if commentid == "" or commentid == None:
            flash('Comment not found to edit')
        else:
            comment = request.form['editedcomment']
            if request.form['submit'] == 'deleteComment':
                User(session['uid']).delete_comment(commentid)
                flash('Your post has been deleted')
            elif request.form['submit'] == 'editComment':
                if comment == "" or comment == None:
                    flash('Comment can not be empty')
                else:
                    User(session['uid']).edit_comment(comment, commentid)
                    flash('Your comment has been updated')
    return redirect(request.referrer)


@social.route('/edit_or_delete_system_comment', methods=['POST'])
#######################################################################################
# function : edit_or_delete_system_comment
# purpose : edits or delete existing comments using unique comment id
# parameters : None
# returns: calls index function
# Exception : None
#######################################################################################
def edit_or_delete_system_comment():
    if session.get('uid') is not None:
        commentid = request.form['commentid']
        system_uid = request.form['system_uid']
        if commentid == "" or commentid == None:
            flash('Comment not found to edit')
            return redirect(url_for('social.view_system', system_uid=system_uid))
        else:
            comment = request.form['editedcomment']
            if request.form['submit'] == 'deleteComment':
                System().delete_system_comment(commentid)
                flash('Your post has been deleted')
            elif request.form['submit'] == 'editComment':
                if comment == "" or comment == None:
                    flash('Comment can not be empty')
                else:
                    System().edit_system_comment(comment, commentid)
                    flash('Your comment has been updated')
    return redirect(url_for('social.view_system', system_uid=system_uid))


social.route('/edit_comment', methods=['POST'])


#######################################################################################
# function : edit_comment
# purpose : edits comments using unique comment id
# parameters : None
# returns: calls index function
# Exception : None
#######################################################################################
def edit_comment():
    if session.get('uid') is not None:
        commentid = request.form['commentid']
        if commentid == "" or commentid == None:
            flash('Comment not found to edit')
        else:
            comment = request.form['editedcomment']
            if comment == "" or comment == None:
                flash('Comment can not be empty')
            else:
                User(session['uid']).edit_comment(comment, commentid)
                flash('Your comment has been updated')
    return redirect(request.referrer)


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
    elif postid == "" or postid == None:
        flash('Post not found to edit')
    else:
        User(session['uid']).edit_post(newpost, postid)
        flash('Your comment has been updated')
    return redirect(request.referrer)


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
    if session.get('uid') is None:
        return redirect_to_page('home')

    # getting profile's google id and checking if it is a post
    google_id = request.form.get('google_id')
    # getting page type: home or profile
    page_type = request.form.get('page_type')
    if request.method != 'POST':
        return redirect_to_page(page_type, google_id)

    text = request.form['text']
    if text == "":
        flash('Post cannot be empty.')
        return redirect_to_page(page_type, google_id)

    user = User(session['uid'])
    privacy = request.form['privacy']
    link = request.form['link']

    user_profile = None
    if page_type == 'profile':
        user_profile = user.get_user_by_google_id(google_id)
    if user_profile and user_profile.one:
        user_profile = user_profile.one

    user.add_post(text, privacy, link, user_profile)
    flash('Your post has been shared')
    return redirect_to_page(page_type, google_id)


#######################################################################################
#######################################################################################
# function : redirect_to_page
# purpose : returns the redirection url for the given parameters
# parameters : page, argument
# returns: response object (a WSGI application)
# Exception : None
#######################################################################################
def redirect_to_page(page, argument=""):
    if page == "home":
        return redirect(url_for('social.index'))
    if page == "profile":
        return redirect(url_for('social.profile', google_id=argument))


#######################################################################################
# function : add_system_post
# purpose : renders system_social.html
# parameters : system_uid
# returns: system_social.html
# Exception : General Exception
#######################################################################################
@social.route('/systems/add_system_post', methods=['POST'])
def add_system_post():
    user_sql_id = session.get('uid')
    if user_sql_id is None:
        return redirect(url_for('social.systems'))
    system = System()
    if request.method == 'POST':
        system_uid = request.form['system_uid']
        print("Creating the new system post")
        print(system_uid)
        system_neo4j = system.get_system_by_uid(system_uid)
        # InValid System_UID
        if not system_neo4j:
            flash('System not found in neo4j.')
            return redirect(url_for('social.view_system', system_uid=system_uid))
            # Valid System_UID
        else:
            logged_in_user = User(user_sql_id).find()
            created_date = convert_milliseconds_to_normal_date(system_neo4j[0][0]['creation_time'])
            privacy = request.form['privacy']
            text = request.form['text']
            link = request.form['link']
            if text == "":
                flash('Post cannot be empty.')
            else:
                System().add_system_post(system_uid, user_sql_id, text, privacy, link)
    return redirect(url_for('social.view_system', system_uid=system_uid))


@social.route('/like_or_unlike_post', methods=['POST'])
#######################################################################################
# function : like_or_unlike_post
# purpose : like or unlike existing post using unique post id
# parameters : None
# returns: calls index function
# Exception : None
#######################################################################################
def like_or_unlike_post():
    if request.method == 'POST':
        if session.get('uid') is not None:
            postid = request.form['postid']
            print('This is a post i')
            print(postid)

            print(request.form['submit'])
            if postid == "":
                flash('Can not find the post to delete.')
            else:
                if request.form['submit'] == 'likePost':
                    User(session['uid']).like_post(postid)
                    flash('You liked the post')
                elif request.form['submit'] == 'unlikePost':
                    User(session['uid']).unlike_post(postid)
                    flash('You unliked the post')
            return redirect(request.referrer)


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
    return redirect(request.referrer)


@social.route('/add_system_comment', methods=['POST'])
#######################################################################################
# function : add_system_comment
# purpose : adds comments to the post
# parameters : None
# returns: calls index function
# Exception : None
#######################################################################################
def add_system_comment():
    comment = request.form['newcomment']
    postid = request.form['postid']
    userid = session['uid']
    system_uid = request.form['system_uid']
    if comment == "" or comment == None:
        flash('Comment can not be empty')
        redirect(url_for('social.view_system', system_uid=system_uid))
    elif postid == "" or postid == None:
        flash('Post not found to comment on')
        redirect(url_for('social.view_system', system_uid=system_uid))
    else:
        System().add_system_comment(userid, comment, postid)
        flash('Your comment has been posted')
    return redirect(url_for('social.view_system', system_uid=system_uid))


@social.route('/edit_system_post', methods=['POST'])
#######################################################################################
# function : edit_system_post
# purpose : edits existing system comments using unique comment id
# parameters : None
# returns: calls index function
# Exception : None
#######################################################################################
def edit_system_post():
    newpost = request.form['editedpost']
    postid = request.form['postid']
    system_uid = request.form['system_uid']

    if newpost == "" or newpost == None:
        flash('New post can not be empty')
        redirect(url_for('social.view_system', system_uid=system_uid))
    elif postid == "" or postid == None:
        flash('Post not found to edit')
        redirect(url_for('social.view_system', system_uid=system_uid))
    else:
        System().edit_system_post(newpost, postid)
        flash('Your comment has been updated')
    return redirect(url_for('social.view_system', system_uid=system_uid))


@social.route('/delete_system_post', methods=['POST'])
#######################################################################################
# function : delete_system_post
# purpose : deletes existing system post using unique post id
# parameters : None
# returns: calls system timeline function
# Exception : None
#######################################################################################
def delete_system_post():
    postid = request.form['postid']
    system_uid = request.form['system_uid']
    if postid == "" or postid == None:
        flash('Post not found to delete')
        redirect(url_for('social.view_system', system_uid=system_uid))
    else:
        System().delete_system_post(postid)
        flash('Your comment has been updated')
    return redirect(url_for('social.view_system', system_uid=system_uid))


@social.route('/like_or_unlike_system_post', methods=['POST'])
#######################################################################################
# function : like_or_unlike_system_post
# purpose : like or unlike existing post using unique post id
# parameters : None
# returns: calls index function
# Exception : None
#######################################################################################
def like_or_unlike_system_post():
    if request.method == 'POST':
        if session.get('uid') is not None:
            postid = request.form['postid']
            print('This is a post i')
            print(postid)
            userid = session['uid']
            system_uid = request.form['system_uid']
            print("User id = " + str(userid))
            print("system_uid id = " + str(system_uid))
            print(request.form['submit'])
            if postid == "":
                flash('Can not find the post to delete.')
            else:
                if request.form['submit'] == 'likePost':
                    System().like_system_post(userid, postid)
                    flash('You liked the post')
                elif request.form['submit'] == 'unlikePost':
                    System().unlike_system_post(userid, postid)
                    flash('You unliked the post')
    return redirect(url_for('social.view_system', system_uid=system_uid))


@social.route('/like_system_post', methods=['POST'])
#######################################################################################
# function : like_system_post
# purpose : like system posts previously created by user
# parameters : None
# returns: calls index function
# Exception : None
#######################################################################################
def like_system_post():
    if session.get('uid') is not None:
        userid = session.get('uid')
        postid = request.form['postid']
        system_uid = request.form['system_uid']
        System().like_system_post(userid, postid)
        flash('You liked the post')
        return redirect(url_for('social.view_system', system_uid=system_uid))
    else:
        return render_template("/home.html")


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
    users = User(session['uid']).get_my_friends()
    user_list = []
    sentreq_res, receivedreq_res, frnds_res = User(session['uid']).get_friends_and_sent_req()
    for result in users:
        individual_user = {}
        first_name = result[0]
        last_name = result[1]
        org = result[2]
        user_sql_id = result[3]
        email = result[4]
        gid = result[5]
        friend_status = "Add Friend"
        for sf in sentreq_res:
            sf_id = sf[0]
            if (user_sql_id == sf_id):
                friend_status = "Sent Friend Request"
        for rf in receivedreq_res:
            rf_id = rf[0]
            if (user_sql_id == rf_id):
                friend_status = "Received Friend Request"
        for fr in frnds_res:
            fr_id = fr[0]
            if (user_sql_id == fr_id):
                friend_status = "Friends"
        if (user_sql_id == session['uid']):
            friend_status = ""

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
        individual_user['gid'] = gid
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
    session.pop('access_token', None)
    session.pop('token', None)
    session.pop('uid', None)
    session.pop('img', None)
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
# API call to update system node in the Neo4J database using system_uid
######################################################################
@social.route('/aqxapi/post/system', methods=['POST'])
def update_system():
    jsonObject = request.get_json()
    return ScAPI(getGraphConnectionURI()).update_system_with_system_uid(jsonObject)


######################################################################
# API call to delete system node in the Neo4J database
######################################################################
@social.route('/aqxapi/delete/system/<system_id>', methods=['DELETE'])
def delete_system_by_system_id(system_id):
    if session.get('siteadmin') is not None:
        return ScAPI(getGraphConnectionURI()).delete_system_by_system_id(system_id)


######################################################################
# API call to get the system(s) node for the user related to from the Neo4J database
######################################################################
@social.route('/aqxapi/get/system/for_user/<sql_id>', methods=['GET'])
def get_system_for_user(sql_id):
    return ScAPI(getGraphConnectionURI()).get_system_for_user(sql_id)


#######################################################################################

@social.route('/test_add_post', methods=['POST'])
#######################################################################################
# function : test_add_post
# purpose : tests adds posts newly created by user
# parameters : None
# returns: calls index function
# Exception : None
#######################################################################################
def test_add_post():
    if session.get('uid') is not None:
        privacy = request.form['privacy']
        text = request.form['text']
        link = request.form['link']
        if text == "":
            flash('Post cannot be empty.')
        else:
            User(session['uid']).test_add_post(text, privacy, link)
            flash('Your post has been shared')
    return redirect(url_for('social.index'))


@social.route('/test_add_comment', methods=['POST'])
#######################################################################################
# function : test_add_comment
# purpose : tests adds comments to the post
# parameters : None
# returns: calls index function
# Exception : None
#######################################################################################
def test_add_comment():
    comment = request.form['newcomment']
    postid = request.form['postid']
    if comment == "" or comment == None:
        flash('Comment can not be empty')
        redirect(url_for('social.index'))
    elif postid == "" or postid == None:
        flash('Post not found to comment on')
        redirect(url_for('social.index'))
    else:
        User(session['uid']).test_add_comment(comment, postid)
        flash('Your comment has been posted')
    return redirect(url_for('social.index'))


#######################################################################################
# function : checkStatus
# purpose : check the status of a user with another user
# parameters : None
# returns: if the user is friend,pending friend,add as a friend.
# Exception : None
#######################################################################################
def checkStatus(user_sql_id):
    friend_status = "Add friend"
    sentreq_res, receivedreq_res, frnds_res = User(session['uid']).get_friends_and_sent_req()
    for sf in sentreq_res:
        sf_id = sf[0]
        if user_sql_id == sf_id:
            friend_status = "Sent Friend Request"
    for rf in receivedreq_res:
        rf_id = rf[0]
        if user_sql_id == rf_id:
            friend_status = "Received Friend Request"
    for fr in frnds_res:
        fr_id = fr[0]
        if user_sql_id == fr_id:
            friend_status = "Friends"
    if user_sql_id == session['uid']:
        friend_status = "Me"
    return friend_status
