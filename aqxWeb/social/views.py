from flask import Blueprint, request, session, redirect, url_for, render_template, flash, Response, jsonify, json, current_app, abort
from flask_login import login_required
import mysql.connector
import requests
from flask_oauth import OAuth
import json
import datetime

from aqxWeb.social.models import User, get_all_recent_posts, get_all_recent_comments, get_all_recent_likes
from aqxWeb.social.models import get_total_likes_for_posts, get_all_post_owners, get_system_measurements_dav_api
from aqxWeb.social.models import System, Privacy, Group
from aqxWeb.social.models import social_graph
from aqxWeb.social.models import get_all_profile_posts
from aqxWeb.social.models import convert_milliseconds_to_normal_date, get_address_from_lat_lng

from aqxWeb.social.api import SocialAPI
import aqxWeb.social.models as models
import aqxWeb.social.aqxdb as aqxdb

social = Blueprint('social', __name__, template_folder='templates', static_folder="static")


def dbconn():
    return mysql.connector.connect(user=current_app.config['USER'],
                                   password=current_app.config['PASS'],
                                   host=current_app.config['HOST'],
                                   database=current_app.config['DB'])


@social.route('/index')
def index():
    if session.get('uid') is None:
        return redirect(url_for('index'))  # if no session, return to login
    posts = get_all_recent_posts(session.get('uid'))
    comments = get_all_recent_comments()
    likes = get_all_recent_likes()
    total_likes = get_total_likes_for_posts()
    post_owners = get_all_post_owners()
    privacy = Privacy([Privacy.FRIENDS, Privacy.PUBLIC], Privacy.FRIENDS,
                      'home', session['uid'])  # info about timeline/page)
    privacy.user_relation = None
    admin_systems = System().get_admin_systems(session['uid'])
    return render_template('home.html', posts=posts, comments=comments,
                           privacy_info=privacy, likes=likes,
                           total_likes=total_likes, post_owners=post_owners,
                           admin_systems=admin_systems)


@social.route('/signin')
def signin():
    try:
        access_token = session.get('access_token')
        access_token = access_token[0]
        r = requests.get('https://www.googleapis.com/plus/v1/people/me?access_token=' + access_token)
        google_api_response = json.loads(r.content)
        current_app.logger.debug("signed in: %s", str(google_api_response))
        google_id = google_api_response['id']
        if 'image' in google_api_response:
            image = google_api_response['image']
            imgurl = image['url']
        else:
            imgurl = "/static/images/default_profile.png"
        session['img'] = imgurl
        user_id = get_user(google_id, google_api_response)
        emails = google_api_response['emails']
        email = emails[0]['value']
        current_app.logger.debug("user: %s img: %s", user_id, imgurl)
        return redirect(url_for('social.index'))
    except:
        current_app.logger.exception("Got an exception")
        raise


def get_user(google_id, google_api_response):
    conn = dbconn()
    cursor = conn.cursor()
    try:
        userId = aqxdb.get_or_create_user(conn, cursor, google_id, google_api_response)
        return userId
    finally:
        conn.close()


def get_google_profile(google_id, user_profile=None):
    try:
        access_token = session.get('access_token')
        access_token = access_token[0]
        r = requests.get('https://www.googleapis.com/plus/v1/people/' + google_id + '?access_token=' + access_token)

        google_profile = {
            "google_id": google_id
        }

        google_response = json.loads(r.content)
        if google_response and not google_response.get('error'):
            current_app.logger.debug("profile of: %s", str(google_response))

            img_url = None
            google_plus_account_url = google_response.get("url", None)
            plus_url = ""
            # getting image url
            if 'image' in google_response:
                image = google_response['image']
                img_url = image['url'].replace('?sz=50', '')

            if google_plus_account_url is not None:
                plus_url = google_response.get('url')

            if google_response.get('displayName'):
                google_profile = {
                    "google_id": google_id,
                    "displayName": google_response.get('displayName'),
                    "plus_url": plus_url,
                    "img_url": img_url
                }
            else:
                google_profile = get_alternative_google_profile(user_profile)

        return google_profile
    except Exception as e:
        current_app.logger.exception("Exception at get_google_profile: " + str(e))


def get_alternative_google_profile(user_profile):
    if user_profile:
        display_name = user_profile['displayName']
        if not display_name:
            display_name = user_profile['email']
            display_name = display_name.split('@', 1)[0]
        google_profile = {
            "displayName": display_name,
            "google_id": user_profile['google_id'],
            "plus_url": "#",
            "img_url": ""
        }
    return google_profile


@social.route('/editprofile')
def editprofile():
    sql_id = session.get('uid')
    if sql_id is not None:
        user = User(sql_id).find()
        return render_template("profile_edit.html", user=user)
    else:
        return render_template("/home.html")


@social.route('/updateprofile', methods=['POST'])
def updateprofile():
    try:
        sql_id = session.get('uid')
        if sql_id is None:
            return redirect(url_for('social.index'))
        given_name = request.form.get('givenName', None)
        family_name = request.form.get('familyName', None)
        display_name = request.form.get('displayName', None)
        gender = request.form.get('gender', None)
        organization = request.form.get('organization', None)
        user_type = request.form.get('user_type', None)
        date_of_birth = request.form.get('dob', None)
        User(sql_id).update_profile(given_name, family_name, display_name, gender, organization, user_type,
                                    date_of_birth)
        session['displayName'] = display_name
        flash("User Profile Updated successfully!")
        return editprofile()
    except Exception as ex:
        current_app.logger.exception("Exception Occurred At updateprofile: ", ex)


@social.route('/profile/<google_id>', methods=['GET'])
def profile(google_id):
    if session.get('uid') is None:
        return redirect(url_for('social.index'))

    try:
        # getting data from neo4j
        if google_id == "me":
            sql_id = session['uid']
            status = "Me"
        else:
            sql_id = models.get_sql_id(google_id)
            if sql_id is None:
                return redirect(url_for('social/Home'))
            else:
                status = User(session['uid']).check_status(session['uid'], sql_id)

        admin_systems = System().get_admin_systems(sql_id)
        participated_systems = System().get_participated_systems(sql_id)
        subscribed_systems = System().get_subscribed_systems(sql_id)
        friends = User(sql_id).get_my_friends(sql_id)

        # Invalid User
        user_profile = User(sql_id).find()
        if user_profile is None:
            return redirect(url_for('social.home'))
        else:
            # accessing google API to retrieve profile data
            google_profile = get_google_profile(google_id, user_profile)
            privacy = get_user_privacy(sql_id)
            posts = get_all_profile_posts(sql_id)
            total_likes = get_total_likes_for_posts()
            likes = get_all_recent_likes()
            stop_at = 3
            return render_template("profile.html", user_profile=user_profile, google_profile=google_profile,
                                   posts=posts, privacy_info=privacy, likes=likes, total_likes=total_likes,
                                   participated_systems=participated_systems, subscribed_systems=subscribed_systems,
                                   admin_systems=admin_systems, friends=friends, status=status, sql_id=sql_id,
                                   stop_at=stop_at)

    except Exception as e:
        current_app.logger.exception("Exception at view_profile: " + str(e))


def get_user_privacy(sql_id):
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
    return privacy


# @social.route('/friends', methods=['GET'])
# def friends():
#    if session.get('uid') is not None:
#        return render_template("friends.html")
#    else:
#        return render_template("/home.html")


@social.route('/accept_friend_request/<u_sql_id>', methods=['GET', 'POST'])
def accept_friend_request(u_sql_id):
    accepted_sql_id = u_sql_id
    User(session['uid']).accept_friend_request(accepted_sql_id)
    User(session['uid']).delete_friend_request(accepted_sql_id)
    flash('Friend Request Accepted');
    return redirect(url_for('social.pendingRequest'))


@social.route('/decline_friend_request/<u_sql_id>', methods=['GET', 'POST'])
def decline_friend_request(u_sql_id):
    accepted_sql_id = u_sql_id
    User(session['uid']).delete_friend_request(accepted_sql_id)
    flash('Friend Request Deleted');
    return redirect(url_for('social.pendingRequest'))


@social.route('/block_friend/<u_sql_id>', methods=['GET', 'POST'])
def block_friend(u_sql_id):
    blocked_sql_id = u_sql_id
    User(session['uid']).block_a_friend(blocked_sql_id)
    flash('Friend Blocked');
    return redirect(url_for('social.friends'))


@social.route('/unblock_friend/<u_sql_id>', methods=['GET', 'POST'])
def unblock_friend(u_sql_id):
    blocked_sql_id = u_sql_id
    User(session['uid']).unblock_a_friend(blocked_sql_id)
    flash('Friend Blocked');
    return redirect(url_for('social.friends'))


@social.route('/delete_friend/<u_sql_id>', methods=['GET', 'POST'])
def delete_friend(u_sql_id):
    accepted_sql_id = u_sql_id
    User(session['uid']).delete_friend(accepted_sql_id)
    flash('Friend  Deleted');
    return redirect(url_for('social.friends'))


@social.route('/delete_friend_timeline/<u_sql_id>', methods=['GET', 'POST'])
def delete_friend_timeline(u_sql_id):
    accepted_sql_id = u_sql_id
    User(session['uid']).delete_friend(accepted_sql_id)
    flash('Friend  Deleted');
    return redirect(User(session['uid']).redirect_url())


@social.route('/friends', methods=['GET', 'POST'])
def friends():
    if session.get('uid') is None:
        return redirect(url_for('social.index'))
    if request.method == 'GET':
        u_sql_id = User(session['uid']).get_user_sql_id()
        Friends = User(session['uid']).get_my_friends(u_sql_id);
        UnblockedFriend = User(session['uid']).get_my_blocked_friends(u_sql_id);
        return render_template("/friends.html", Friends=Friends, UnblockedFriend=UnblockedFriend)


@social.route('/pendingRequest', methods=['GET', 'POST'])
def pendingRequest():
    if request.method == 'GET':
        if session.get('uid') is not None:
            u_sql_id = User(session['uid']).get_user_sql_id()
            pendingRequests = User(session['uid']).get_pending_friend_request(u_sql_id);
            return render_template("/pendingRequest.html", pendingRequests=pendingRequests)

    else:
        return render_template("/home.html")


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


@social.route('/searchFriends', methods=['GET'])
def searchFriends():
    if session.get('uid') is not None:
        return render_template("search_friends.html")
    else:
        return render_template("/home.html")


@social.route('/send_friend_request/<u_sql_id>', methods=['POST'])
def send_friend_request(u_sql_id):
    receiver_sql_id = u_sql_id
    User(session['uid']).send_friend_request(receiver_sql_id)
    return redirect(url_for('social.friends'))


@social.route('/send_friend_request_timeline/<u_sql_id>', methods=['GET', 'POST'])
def send_friend_request_timeline(u_sql_id):
    receiver_sql_id = u_sql_id
    User(session['uid']).send_friend_request(receiver_sql_id)
    return redirect(User(session['uid']).redirect_url())


@social.route('/systems', methods=['GET', 'POST'])
@social.route('/systems/', methods=['GET', 'POST'])
def search_systems():
    sql_id = session.get('uid')
    if sql_id is None:
        return redirect(url_for('social.index'))
    else:
        if request.method == 'POST':
            systemName = request.form['txtSystemName']
            system_search_results = System().get_system_by_name(systemName)
            return render_template("system_search.html", post_method="true", search_param=systemName,
                                   system_search_results=system_search_results)
        elif request.method == 'GET':
            return render_template("system_search.html")


@social.route('/systems/self', methods=['GET'])
def self_systems():
    sql_id = session.get('uid')
    if sql_id is None:
        return redirect(url_for('social.index'))
    else:
        if request.method == 'GET':
            admin_systems = System().get_admin_systems(sql_id)
            participated_systems = System().get_participated_systems(sql_id)
            subscribed_systems = System().get_subscribed_systems(sql_id)
            recommended_systems = System().get_recommended_systems(sql_id)
            return render_template("system_self.html", admin_systems=admin_systems,
                                   participated_systems=participated_systems, subscribed_systems=subscribed_systems,
                                   recommended_systems=recommended_systems)


@social.route('/systems/all', methods=['GET'])
def all_systems_neo4j():
    sql_id = session.get('uid')
    if sql_id is None:
        return redirect(url_for('social.index'))
    else:
        if request.method == 'GET':
            all_systems = System().get_all_systems()
            return render_template("system_all.html", all_systems=all_systems)


@social.route('/systems/<system_uid>', methods=['GET'])
def view_system(system_uid):
    user_sql_id = session.get('uid')
    if user_sql_id is None:
        # not logged in -> redirect to the system overview
        return redirect(url_for('frontend.sys_overview', system_uid=system_uid))

    system = System()
    system_neo4j = system.get_system_by_uid(system_uid)
    if not system_neo4j:
        abort(404)

    # otherwise continue
    logged_in_user = User(user_sql_id).find()
    created_date = convert_milliseconds_to_normal_date(system_neo4j[0][0]['creation_time'])
    system_location = get_address_from_lat_lng(system_neo4j[0][0]['location_lat'],
                                               system_neo4j[0][0]['location_lng'])
    system_mysql = system_neo4j
    user_privilege = system.get_user_privilege_for_system(user_sql_id, system_uid)
    system_admins = system.get_system_admins(system_uid)
    display_names = [a['user']['displayName'] for a in system_admins]
    system_admin_str = ', '.join(display_names)
    system_participants = system.get_system_participants(system_uid)
    system_subscribers = system.get_system_subscribers(system_uid)
    participants_pending_approval = system.get_participants_pending_approval(system_uid)
    subscribers_pending_approval = system.get_subscribers_pending_approval(system_uid)
    if user_privilege == "SYS_ADMIN" or user_privilege == "SYS_PARTICIPANT":
        privacy_options = [Privacy.PARTICIPANTS, Privacy.PUBLIC]
        privacy_default = Privacy.PARTICIPANTS
    else:
        privacy_options = [Privacy.PUBLIC]
        privacy_default = Privacy.PUBLIC

    privacy = Privacy(privacy_options, privacy_default, 'system_social', user_sql_id)
    posts = system.get_system_recent_posts(system_uid)
    comments = system.get_system_recent_comments(system_uid)
    likes = system.get_system_recent_likes(system_uid)
    total_likes = system.get_total_likes_for_system_posts(system_uid)
    post_owners = system.get_system_post_owners(system_uid)
    measurements_output_dav = get_system_measurements_dav_api(system_uid)
    json_output_measurement = json.loads(measurements_output_dav)
    measurements = None
    if "error" not in json_output_measurement:
        measurements = json_output_measurement['measurements']
    return render_template("system_social.html",
                           system_neo4j=system_neo4j,
                           system_mysql=system_mysql,
                           logged_in_user=logged_in_user,
                           created_date=created_date,
                           system_location=system_location,
                           user_privilege=user_privilege,
                           system_admins=system_admins,
                           system_participants=system_participants,
                           system_subscribers=system_subscribers,
                           participants_pending_approval=participants_pending_approval,
                           subscribers_pending_approval=subscribers_pending_approval,
                           system_uid=system_uid,
                           privacy_info=privacy,
                           posts=posts,
                           comments=comments,
                           likes=likes,
                           total_likes=total_likes,
                           post_owners=post_owners,
                           measurements=measurements,
                           system_admin_str=system_admin_str)


@social.route('/systems/approve_reject_participant', methods=['POST'])
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
        return redirect(url_for('social.manage_system', system_uid=system_uid))
    else:
        return redirect(url_for('social.search_systems'))


@social.route('/systems/participate_subscribe_leave', methods=['POST'])
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


@social.route('/manage/systems/<system_uid>', methods=['GET', 'POST'])
def manage_system(system_uid):
    sql_id = session.get('uid')
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


@social.route('/manage/systems/delete_system_participant_or_make_admin', methods=['POST'])
def delete_system_participant_or_make_admin():
    if request.method == 'POST':
        system_uid = request.form["system_uid"]
        google_id = request.form["google_id"]
        system = System()
        sql_id = session.get('uid')
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


@social.route('/manage/systems/delete_admin', methods=['POST'])
def delete_system_admin():
    if request.method == 'POST':
        system_uid = request.form["system_uid"]
        google_id = request.form["google_id"]
        system = System()
        sql_id = session.get('uid')
        if sql_id is not None:
            user_privilege = system.get_user_privilege_for_system(sql_id, system_uid)
            if user_privilege == "SYS_ADMIN":
                if request.form['submit'] == 'DeleteAdmin':
                    system.delete_system_admin(google_id, system_uid)
        return redirect(url_for('social.manage_system', system_uid=system_uid))
    else:
        return redirect(url_for('social.search_systems'))


@social.route('/manage/systems/delete_system_subscriber_or_make_admin', methods=['POST'])
def delete_system_subscriber_or_make_admin():
    if request.method == 'POST':
        system_uid = request.form["system_uid"]
        google_id = request.form["google_id"]
        system = System()
        sql_id = session.get('uid')
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


@social.route('/groups', methods=['GET'])
@social.route('/groups/', methods=['GET'])
def groups():
    sql_id = session.get('uid')
    if sql_id is None:
        return redirect(url_for('social.index'))
    else:
        if request.method == 'GET':
            group = Group()
            return render_template("groups.html")


@social.route('/groups/self', methods=['GET'])
def self_groups():
    sql_id = session.get('uid')
    if sql_id is None:
        return redirect(url_for('social.index'))
    else:
        if request.method == 'GET':
            group = Group()
            admin_groups = group.get_admin_groups(sql_id)
            member_groups = group.get_member_groups(sql_id)
            return render_template("group_self.html", admin_groups=admin_groups, member_groups=member_groups)


@social.route('/groups/search', methods=['GET'])
def search_groups():
    sql_id = session.get('uid')
    if sql_id is None:
        return redirect(url_for('social.index'))
    else:
        if request.method == 'GET':
            group = Group()
            return render_template("group_search.html")


@social.route('/groups/recommended', methods=['GET'])
def recommended_groups():
    sql_id = session.get('uid')
    if sql_id is None:
        return redirect(url_for('social.index'))
    else:
        if request.method == 'GET':
            group = Group()
            recommended_groups = group.get_recommended_groups(sql_id)
            return render_template("group_recommended.html", recommended_groups=recommended_groups)


@social.route('/get_groups', methods=['GET'])
def get_groups():
    groups = Group().get_groups()
    grp_list = []
    for res in groups:
        individual_grp = {}
        grp_name = res[0]
        grp_desc = res[1]
        grp_uid = res[2]
        individual_grp['label'] = grp_name
        individual_grp['desc'] = grp_desc
        individual_grp['uid'] = grp_uid
        grp_list.append(individual_grp)
    return jsonify(json_list=grp_list)


@social.route('/groups/<group_uid>', methods=['GET', 'POST'])
def view_group(group_uid):
    sql_id = session.get('uid')
    if sql_id is None:
        return redirect(url_for('social.index'))
    try:
        group = Group()
        if request.method == 'GET':
            group_neo4j = group.get_group_by_uid(group_uid)
            # InValid Group_UID
            if not group_neo4j:
                return redirect(url_for('social.groups'))
            # Valid Group_UID
            else:
                logged_in_user = User(sql_id).find()
                user_privilege = group.get_user_privilege_for_group(sql_id, group_uid)
                group_members = group.get_group_members(group_uid)
                members_pending_approval = group.get_members_pending_approval(group_uid)
                creation_date = convert_milliseconds_to_normal_date(group_neo4j[0][0]['creation_time'])
                if user_privilege == "GROUP_ADMIN" or user_privilege == "GROUP_MEMBER":
                    privacy_options = [Privacy.PARTICIPANTS, Privacy.PUBLIC]
                    privacy_default = Privacy.PARTICIPANTS
                else:
                    privacy_options = [Privacy.PUBLIC]
                    privacy_default = Privacy.PUBLIC

                privacy = Privacy(privacy_options, privacy_default, 'groups', sql_id)
                posts = group.get_group_recent_posts(group_uid)
                comments = group.get_group_recent_comments(group_uid)
                likes = group.get_group_recent_likes(group_uid)
                total_likes = group.get_total_likes_for_group_posts(group_uid)
                post_owners = group.get_group_post_owners(group_uid)
                return render_template("group_social.html", group_neo4j=group_neo4j, logged_in_user=logged_in_user,
                                       user_privilege=user_privilege, group_members=group_members, stop_at=3,
                                       members_pending_approval=members_pending_approval, creation_date=creation_date,
                                       privacy_info=privacy, posts=posts, comments=comments, likes=likes,
                                       total_likes=total_likes, post_owners=post_owners, group_uid=group_uid)
    except Exception as e:
        current_app.logger.exception("Exception at view_group: " + str(e))


@social.route('/groups/get_users_to_invite_groups/<group_uid>', methods=['GET'])
def get_users_to_invite_groups(group_uid):
    try:
        sql_id = session.get('uid')
        if sql_id is None:
            return redirect(url_for('social.index'))
        group = Group()
        users_not_part_of_group = group.get_users_to_invite_groups(group_uid)
        user_list = []
        for user in users_not_part_of_group:
            individual_user = {}

            individual_user['google_id'] = user[0]["google_id"]

            if user[0]["givenName"] is not None:
                individual_user['givenName'] = user[0]["givenName"]
                individual_user['label'] = user[0]["givenName"]
            else:
                individual_user['givenName'] = "No Given Name"
                individual_user['label'] = user[0]["givenName"]

            if user[0]["familyName"] is not None:
                individual_user['familyName'] = user[0]["familyName"]
            else:
                individual_user['familyName'] = ""

            if user[0]["organization"] is not None:
                individual_user['organization'] = user[0]["organization"]
            else:
                individual_user['organization'] = ""

            if user[0]["image_url"] is not None:
                individual_user['image_url'] = user[0]["image_url"]
            else:
                individual_user['image_url'] = ""

            user_list.append(individual_user)
        return jsonify(user_json_list=user_list)
    except Exception as ex:
        current_app.logger.exception("Exception at get_users_to_invite_groups: ", ex)
        user_list = []
        return jsonify(user_json_list=user_list)


@social.route('/manage/groups/<group_uid>', methods=['GET', 'POST'])
def manage_group(group_uid):
    sql_id = session.get('uid')
    if sql_id is None:
        return redirect(url_for('social.index'))
    group = Group()
    logged_in_user = User(sql_id).find()
    group_neo4j = group.get_group_by_uid(group_uid)
    # InValid Group_UID
    if not group_neo4j:
        return redirect(url_for('social.groups'))
    user_privilege = group.get_user_privilege_for_group(sql_id, group_uid)
    # Only Admin of The Group Has Privileges To Access The Settings Page
    if user_privilege != "GROUP_ADMIN":
        return redirect(url_for('social.groups'))
    if request.method == 'GET':
        members_pending_approval = group.get_members_pending_approval(group_uid)
        group_admins = group.get_group_admins(group_uid)
        group_members = group.get_group_members(group_uid)
        return render_template("group_manage.html", group_neo4j=group_neo4j, logged_in_user=logged_in_user,
                               members_pending_approval=members_pending_approval, group_admins=group_admins,
                               group_members=group_members)
    elif request.method == 'POST':
        return render_template("group_manage.html")


@social.route('/manage/groups/update_group_info', methods=['POST'])
def update_group_info():
    try:
        if request.method == 'POST':
            group_uid = request.form.get('group_uid', None)
            name = request.form.get('name', None)
            description = request.form.get('description', None)
            is_private_group = request.form.get('is_private_group', None)
            group = Group()
            sql_id = session.get('uid')
            if sql_id is not None and group_uid is not None:
                user_privilege = group.get_user_privilege_for_group(sql_id, group_uid)
                if user_privilege == "GROUP_ADMIN":
                    group.update_group_info(group_uid, name, description, is_private_group)
            flash("Group Information Updated successfully!")
            return redirect(url_for('social.manage_group', group_uid=group_uid))
        else:
            return redirect(url_for('social.groups'))
    except Exception as ex:
        current_app.logger.exception("Exception Occurred at update_group_info: ", ex)


@social.route('/manage/groups/create_group', methods=['POST'])
def create_group():
    sql_id = session.get('uid')
    if sql_id is None:
        return redirect(url_for('social.groups'))
    name = request.form['name']
    description = request.form['description']
    is_private = request.form['is_private_group']
    group = Group()
    if is_private == "" or is_private is None:
        flash('Privacy option can not be empty')

    elif description == "" or description is None:
        flash('Description cannot be empty')

    elif name == "" or name is None:
        flash('Name cannot be empty')

    else:
        group_uid = group.create_group(sql_id, name, description, is_private)
        flash('Your Group has been Successfully Created!')
        return redirect(url_for('social.view_group', group_uid=group_uid))
    return redirect(url_for('social.groups'))


@social.route('/manage/groups/approve_reject_member', methods=['POST'])
def approve_reject_group_member():
    if request.method == 'POST':
        google_id = request.form["google_id"]
        group_uid = request.form["group_uid"]
        group = Group()
        sql_id = session.get('uid')
        if sql_id is not None:
            user_privilege = group.get_user_privilege_for_group(sql_id, group_uid)
            if user_privilege == "GROUP_ADMIN":
                if request.form['submit'] == 'Approve':
                    group.approve_group_member(google_id, group_uid)
                elif request.form['submit'] == 'Reject':
                    group.reject_group_member(google_id, group_uid)
        return redirect(url_for('social.manage_group', group_uid=group_uid))
    else:
        return redirect(url_for('social.groups'))


@social.route('/manage/groups/invite_group_member', methods=['POST'])
def invite_group_member():
    try:
        if request.method == 'POST':
            google_id = request.form["google_id"]
            group_uid = request.form["group_uid"]
            group = Group()
            sql_id = session.get('uid')
            if sql_id is not None:
                user_privilege = group.get_user_privilege_for_group(sql_id, group_uid)
                if user_privilege == "GROUP_ADMIN" or user_privilege == "GROUP_MEMBER":
                    group.approve_group_member(google_id, group_uid)
            return redirect(url_for('social.view_group', group_uid=group_uid))
        else:
            return redirect(url_for('social.groups'))
    except Exception as ex:
        current_app.logger.exception("Exception at invite_group_member: ", ex)
        return redirect(url_for('social.groups'))

@social.route('/manage/groups/delete_group_admin_or_make_member', methods=['POST'])
def delete_group_admin_or_make_member():
    try:
        if request.method == 'POST':
            google_id = request.form["google_id"]
            group_uid = request.form["group_uid"]
            group = Group()
            sql_id = session.get('uid')
            if sql_id is not None:
                user_privilege = group.get_user_privilege_for_group(sql_id, group_uid)
                if user_privilege == "GROUP_ADMIN":
                    if request.form['submit'] == 'MakeMember':
                        group.join_group(google_id, group_uid)
                    elif request.form['submit'] == 'DeleteAdmin':
                        group.delete_group_admin(google_id, group_uid)
            return redirect(url_for('social.manage_group', group_uid=group_uid))
        else:
            return redirect(url_for('social.groups'))
    except Exception as ex:
        current_app.logger.exception("Exception at delete_group_admin_or_make_member: ", ex)


@social.route('/manage/groups/delete_member_or_make_admin', methods=['POST'])
def delete_group_member_or_make_admin():
    if request.method == 'POST':
        google_id = request.form["google_id"]
        group_uid = request.form["group_uid"]
        group = Group()
        sql_id = session.get('uid')
        if sql_id is not None:
            user_privilege = group.get_user_privilege_for_group(sql_id, group_uid)
            if user_privilege == "GROUP_ADMIN":
                if request.form['submit'] == 'MakeAdmin':
                    group.make_admin_for_group(google_id, group_uid)
                elif request.form['submit'] == "DeleteMember":
                    group.delete_group_member(google_id, group_uid)
        return redirect(url_for('social.manage_group', group_uid=group_uid))
    else:
        return redirect(url_for('social.groups'))


@social.route('/manage/groups/join_leave', methods=['POST'])
def join_leave_group():
    if request.method == 'POST':
        group_uid = request.form["group_uid"]
        google_id = request.form["google_id"]
        is_private_group = request.form["is_private_group"]
        group = Group()
        sql_id = session.get('uid')
        if sql_id is not None:
            user_privilege = group.get_user_privilege_for_group(sql_id, group_uid)
            if user_privilege is None:
                if request.form['submit'] == 'Join':
                    if is_private_group == "false":
                        group.join_group(google_id, group_uid)
                    else:
                        group.join_group_pending(google_id, group_uid)
            else:
                if user_privilege == "GROUP_ADMIN" or \
                                user_privilege == "GROUP_PENDING_MEMBER" or \
                                user_privilege == "GROUP_MEMBER":
                    if request.form['submit'] == 'Leave':
                        group.leave_group(google_id, group_uid)
        return redirect(User(session['uid']).redirect_url())


@social.route('/add_comment', methods=['POST'])
def add_comment():
    comment = request.form['newcomment']
    postid = request.form['postid']
    if comment == "" or comment is None:
        flash('Comment can not be empty')
        redirect(request.referrer)
    elif postid == "" or postid is None:
        flash('Post not found to comment on')
        redirect(request.referrer)
    else:
        User(session['uid']).add_comment(comment, postid)
        flash('Your comment has been posted')

    return redirect(request.referrer)


@social.route('/edit_or_delete_comment', methods=['POST'])
def edit_or_delete_comment():
    if session.get('uid') is not None:
        commentid = request.form['commentid']
        # system_uid = request.form["system_uid"]
        if commentid == "" or commentid is None:
            flash('Comment not found to edit')
        else:
            comment = request.form['editedcomment']
            if request.form['submit'] == 'deleteComment':
                User(session['uid']).delete_comment(commentid)
                flash('Your post has been deleted')
            elif request.form['submit'] == 'editComment':
                if comment == "" or comment is None:
                    flash('Comment can not be empty')
                else:
                    User(session['uid']).edit_comment(comment, commentid)
                    flash('Your comment has been updated')
    return redirect(request.referrer)


@social.route('/edit_or_delete_system_comment', methods=['POST'])
def edit_or_delete_system_comment():
    if session.get('uid') is not None:
        comment_id = request.form['commentid']
        system_uid = request.form['system_uid']
        if comment_id == "" or comment_id is None:
            flash('Comment not found to edit')
            return redirect(url_for('social.view_system', system_uid=system_uid))
        else:
            comment = request.form['editedcomment']
            if request.form['submit'] == 'deleteComment':
                System().delete_system_comment(comment_id)
                flash('Your post has been deleted')
            elif request.form['submit'] == 'editComment':
                if comment == "" or comment is None:
                    flash('Comment can not be empty')
                else:
                    System().edit_system_comment(comment, comment_id)
                    flash('Your comment has been updated')
    return redirect(url_for('social.view_system', system_uid=system_uid))


@social.route('/edit_or_delete_group_comment', methods=['POST'])
def edit_or_delete_group_comment():
    if session.get('uid') is not None:
        comment_id = request.form['commentid']
        group_uid = request.form['group_uid']
        if comment_id == "" or comment_id is None:
            flash('Comment not found to edit')
            return redirect(url_for('social.view_group', group_uid=group_uid))
        else:
            comment = request.form['editedcomment']
            if request.form['submit'] == 'deleteComment':
                Group().delete_group_comment(comment_id)
                flash('Your post has been deleted')
            elif request.form['submit'] == 'editComment':
                if comment == "" or comment is None:
                    flash('Comment can not be empty')
                else:
                    Group().edit_group_comment(comment, comment_id)
                    flash('Your comment has been updated')
    return redirect(url_for('social.view_group', group_uid=group_uid))


social.route('/edit_comment', methods=['POST'])
def edit_comment():
    if session.get('uid') is not None:
        comment_id = request.form['commentid']
        if comment_id == "" or comment_id is None:
            flash('Comment not found to edit')
        else:
            comment = request.form['editedcomment']
            if comment == "" or comment is None:
                flash('Comment can not be empty')
            else:
                User(session['uid']).edit_comment(comment, comment_id)
                flash('Your comment has been updated')
    return redirect(request.referrer)


@social.route('/edit_post', methods=['POST'])
def edit_post():
    new_post = request.form['editedpost']
    post_id = request.form['postid']

    if new_post == "" or new_post is None:
        flash('New post can not be empty')
    elif post_id == "" or post_id is None:
        flash('Post not found to edit')
    else:
        User(session['uid']).edit_post(new_post, post_id)
        flash('Your comment has been updated')
    return redirect(request.referrer)


@social.route('/delete_comment', methods=['POST'])
def delete_comment():
    comment_id = request.form['commentid']
    if comment_id == "" or comment_id is None:
        flash('Comment not found to delete')
        redirect(url_for('social.index'))
    else:
        User(session['uid']).delete_comment(comment_id)
        flash('Your comment has been updated')
    return redirect(url_for('social.index'))


@social.route('/add_post', methods=['POST'])
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
    link = request.form.get('link', '')

    user_profile = None
    if page_type == 'profile':
        user_profile = user.get_user_by_google_id(google_id)

    link_title = request.form.get('link_title', '')
    link_img = request.form.get('link_img', '')
    link_description = request.form.get('link_description', '')

    user.add_post(text, privacy, link, user_profile, link_title, link_img, link_description)

    flash('Your post has been shared')
    return redirect_to_page(page_type, google_id)


def redirect_to_page(page, argument=""):
    if page == "home":
        return redirect(url_for('social.index'))
    if page == "profile":
        return redirect(url_for('social.profile', google_id=argument))


@social.route('/systems/add_system_post', methods=['POST'])
def add_system_post():
    user_sql_id = session.get('uid')
    if user_sql_id is None:
        return redirect(url_for('social.systems'))
    system = System()
    if request.method == 'POST':
        system_uid = request.form['system_uid']
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
            link = request.form.get('link', '')
            link_title = request.form.get('link_title', '')
            link_img = request.form.get('link_img', '')
            link_description = request.form.get('link_description', '')

            if text == "":
                flash('Post cannot be empty.')
            else:
                System().add_system_post(system_uid, user_sql_id, text, privacy,
                                         link, link_title, link_img, link_description)
    return redirect(url_for('social.view_system', system_uid=system_uid))


@social.route('/groups/add_group_post', methods=['POST'])
def add_group_post():
    user_sql_id = session.get('uid')
    if user_sql_id is None:
        return redirect(url_for('social.index'))
    group = Group()
    if request.method == 'POST':
        group_uid = request.form['group_uid']
        group_neo4j = group.get_group_by_uid(group_uid)
        # InValid System_UID
        if not group_neo4j:
            flash('Group not found in neo4j.')
            return redirect(url_for('social.view_group', group_uid=group_uid))
            # Valid System_UID
        else:
            logged_in_user = User(user_sql_id).find()
            created_date = convert_milliseconds_to_normal_date(group_neo4j[0][0]['creation_time'])
            privacy = request.form['privacy']
            text = request.form['text']
            link = request.form.get('link', '')
            link_title = request.form.get('link_title', '')
            link_img = request.form.get('link_img', '')
            link_description = request.form.get('link_description', '')

            if text == "":
                flash('Post cannot be empty.')
            else:
                Group().add_group_post(group_uid, user_sql_id, text, privacy,
                                         link, link_title, link_img, link_description)
    return redirect(url_for('social.view_group', group_uid=group_uid))


@social.route('/delete_group_post', methods=['POST'])
def delete_group_post():
    post_id = request.form['postid']
    group_uid = request.form['group_uid']
    if post_id == "" or post_id is None:
        flash('Post not found to delete')
    else:
        Group().delete_group_post(post_id)
        flash('Your comment has been updated')
    return redirect(url_for('social.view_group', group_uid=group_uid))


@social.route('/edit_group_post', methods=['POST'])
def edit_group_post():
    new_post = request.form['editedpost']
    post_id = request.form['postid']
    group_uid = request.form['group_uid']

    if new_post == "" or new_post is None:
        flash('New post can not be empty')
    elif post_id == "" or post_id is None:
        flash('Post not found to edit')
    else:
        Group().edit_group_post(new_post, post_id)
        flash('Your comment has been updated')
    return redirect(url_for('social.view_group', group_uid=group_uid))


@social.route('/like_or_unlike_post', methods=['POST'])
def like_or_unlike_post():
    if request.method == 'POST':
        if session.get('uid') is not None:
            post_id = request.form['postid']
            if post_id == "":
                flash('Can not find the post to delete.')
            else:
                if request.form['submit'] == 'likePost':
                    User(session['uid']).like_post(post_id)
                    flash('You liked the post')
                elif request.form['submit'] == 'unlikePost':
                    User(session['uid']).unlike_post(post_id)
                    flash('You unliked the post')
            return redirect(request.referrer)


@social.route('/delete_post', methods=['POST'])
def delete_post():
    if session.get('uid') is not None:
        post_id = request.form['postid']
        if post_id == "":
            flash('Can not find the post to delete.')
        else:
            User(session['uid']).delete_post(post_id)
            flash('Your post has been deleted')
    return redirect(request.referrer)


@social.route('/add_system_comment', methods=['POST'])
def add_system_comment():
    comment = request.form['newcomment']
    postid = request.form['postid']
    userid = session['uid']
    system_uid = request.form['system_uid']
    if comment == "" or comment is None:
        flash('Comment can not be empty')
        redirect(url_for('social.view_system', system_uid=system_uid))
    elif postid == "" or postid is None:
        flash('Post not found to comment on')
        redirect(url_for('social.view_system', system_uid=system_uid))
    else:
        System().add_system_comment(userid, comment, postid)
        flash('Your comment has been posted')
    return redirect(url_for('social.view_system', system_uid=system_uid))


@social.route('/add_group_comment', methods=['POST'])
def add_group_comment():
    comment = request.form['newcomment']
    postid = request.form['postid']
    userid = session['uid']
    group_uid = request.form['group_uid']
    if comment == "" or comment is None:
        flash('Comment can not be empty')
        redirect(url_for('social.view_group', group_uid=group_uid))
    elif postid == "" or postid is None:
        flash('Post not found to comment on')
        redirect(url_for('social.view_group', group_uid=group_uid))
    else:
        Group().add_group_comment(userid, comment, postid)
        flash('Your comment has been posted')
    return redirect(url_for('social.view_group', group_uid=group_uid))


@social.route('/edit_system_post', methods=['POST'])
def edit_system_post():
    newpost = request.form['editedpost']
    postid = request.form['postid']
    system_uid = request.form['system_uid']

    if newpost == "" or newpost is None:
        flash('New post can not be empty')
        redirect(url_for('social.view_system', system_uid=system_uid))
    elif postid == "" or postid is None:
        flash('Post not found to edit')
        redirect(url_for('social.view_system', system_uid=system_uid))
    else:
        System().edit_system_post(newpost, postid)
        flash('Your comment has been updated')
    return redirect(url_for('social.view_system', system_uid=system_uid))


@social.route('/delete_system_post', methods=['POST'])
def delete_system_post():
    postid = request.form['postid']
    system_uid = request.form['system_uid']
    if postid == "" or postid is None:
        flash('Post not found to delete')
        redirect(url_for('social.view_system', system_uid=system_uid))
    else:
        System().delete_system_post(postid)
        flash('Your comment has been updated')
    return redirect(url_for('social.view_system', system_uid=system_uid))


@social.route('/like_or_unlike_system_post', methods=['POST'])
def like_or_unlike_system_post():
    if request.method == 'POST':
        if session.get('uid') is not None:
            postid = request.form['postid']
            userid = session['uid']
            system_uid = request.form['system_uid']
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


@social.route('/like_or_unlike_group_post', methods=['POST'])
def like_or_unlike_group_post():
    if request.method == 'POST':
        if session.get('uid') is not None:
            post_id = request.form['postid']
            user_id = session['uid']
            group_uid = request.form['group_uid']
            if post_id == "":
                flash('Can not find the post to delete.')
            else:
                if request.form['submit'] == 'likePost':
                    Group().like_group_post(user_id, post_id)
                    flash('You liked the post')
                elif request.form['submit'] == 'unlikePost':
                    Group().unlike_group_post(user_id, post_id)
                    flash('You unliked the post')
    return redirect(url_for('social.view_group', group_uid=group_uid))


@social.route('/like_system_post', methods=['POST'])
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
def like_post():
    if session.get('uid') is not None:
        postid = request.form['postid']
        User(session['uid']).like_post(postid)
        flash('You liked the post')
        return redirect(url_for('social.index'))
    else:
        return render_template("/home.html")


@social.route('/unlike_post', methods=['POST'])
def unlike_post():
    if session.get('uid') is not None:
        postid = request.form['postid']
        User(session['uid']).unlike_post(postid)
        flash('You unliked the post')
        return redirect(url_for('social.index'))
    else:
        return render_template("/home.html")


@social.route('/getfriends', methods=['GET'])
def getfriends():
    users = User(session['uid']).get_search_friends()
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
        friend_status = get_friend_status(user_sql_id, sentreq_res, receivedreq_res, frnds_res)

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
    return jsonify(json_list=user_list)


def get_friend_status(user_sql_id, sentreq_res, receivedreq_res, frnds_res):
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
    return friend_status


@social.route('/logout')
def logout():
    session.pop('access_token', None)
    session.pop('token', None)
    session.pop('uid', None)
    session.pop('img', None)
    session.pop('email', None)
    session.pop('displayName', None)
    return redirect(url_for('index'))


@social.route('/testSignin', methods=['POST'])
def testSignin():
    try:
        GivenName = request.form['givenName']
        familyName = request.form['familyName']
        email = request.form['email']
        user_id = request.form['id']
        user_id = get_user(user_id, email, GivenName, familyName)
        return Response("ok", mimetype='text/plain')
    except:
        current_app.logger.exception("Got an exception")
        raise


######################################################################
# API call to get user data for the specified google_id/sql_id
######################################################################

@social.route('/aqxapi/v1/user', methods=['GET'])
def get_user_by_sql_or_google_id():
    sql_id = request.args.get('sql_id')
    google_id = request.args.get('google_id')
    result = None
    if sql_id is not None:
        result = SocialAPI(social_graph()).get_user_by_sql_id(sql_id)
    elif google_id is not None:
        result = SocialAPI(social_graph()).get_user_by_google_id(google_id)
    # API Status Code For The Results
    if result is None:
        error_msg = json.dumps({'error': 'Invalid request parameters. Required sql_id or google_id'})
        return error_msg, 400
    else:
        if 'error' in result:
            return result, 400
        else:
            return result


@social.route('/aqxapi/v1/user/current', methods=['GET'])
def get_logged_in_user():
    result = SocialAPI(social_graph()).get_logged_in_user()
    if 'error' in result:
        return result, 400
    else:
        return result


@social.route('/aqxapi/v1/user', methods=['POST'])
def create_user():
    jsonObject = request.get_json()
    result = SocialAPI(social_graph()).create_user(jsonObject)
    if 'error' in result:
        return result, 400
    else:
        return result, 201


@social.route('/aqxapi/v1/user', methods=['DELETE'])
def delete_user_by_sql_id():
    sql_id = request.args.get('sql_id')
    if session.get('siteadmin') is not None and sql_id is not None:
        result = SocialAPI(social_graph()).delete_user_by_sql_id(sql_id)
        if 'error' in result:
            return result, 400
        else:
            return result
    else:
        error_msg = json.dumps({'error': 'Privileges/sql_id is missing'})
        return error_msg, 400


@social.route('/aqxapi/v1/system', methods=['POST'])
def sgraph_create_system():
    jsonObject = request.get_json()
    result = SocialAPI(social_graph()).create_system(jsonObject)
    if 'error' in result:
        return result, 400
    else:
        return result, 201


@social.route('/aqxapi/v1/system', methods=['PUT'])
def update_system():
    jsonObject = request.get_json()
    result = SocialAPI(social_graph()).update_system_with_system_uid(jsonObject)
    if 'error' in result:
        return result, 400
    else:
        return result


@social.route('/aqxapi/v1/system', methods=['DELETE'])
def delete_system_by_system_id():
    system_id = request.args.get('system_id')
    if session.get('siteadmin') is not None and system_id is not None:
        result = SocialAPI(social_graph()).delete_system_by_system_id(system_id)
        if 'error' in result:
            return result, 400
        else:
            return result
    else:
        error_msg = json.dumps({'error': 'Privileges/system_id is missing'})
        return error_msg, 400


@social.route('/aqxapi/v1/system', methods=['GET'])
def get_system_for_user():
    sql_id = request.args.get('sql_id')
    if sql_id is not None:
        result = SocialAPI(social_graph()).get_system_for_user(sql_id)
        if 'error' in result:
            return result, 400
        else:
            return result
    else:
        error_msg = json.dumps({'error': 'Invalid request parameters. Required sql_id'})
        return error_msg, 400


@social.route('/test_add_post', methods=['POST'])
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
def test_add_comment():
    comment = request.form['newcomment']
    post_id = request.form['postid']
    if comment == "" or comment is None:
        flash('Comment can not be empty')
        redirect(url_for('social.index'))
    elif post_id == "" or post_id is None:
        flash('Post not found to comment on')
        redirect(url_for('social.index'))
    else:
        User(session['uid']).test_add_comment(comment, post_id)
        flash('Your comment has been posted')
    return redirect(url_for('social.index'))
