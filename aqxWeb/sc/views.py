from flask import Blueprint, Flask, request, session, redirect, url_for, render_template, flash, Response, jsonify
from models import User, get_all_recent_posts, get_all_recent_comments, graph
import mysql.connector
import requests
import aqxdb

social = Blueprint('social', __name__, template_folder='templates')

'''
@social.route('/home')
def home():
    return "hi social"
    '''

#######################################################################################
# function : dbconn
# purpose : Connect with DB
# parameters : None
# returns: DB connection
#######################################################################################
def dbconn():
    return mysql.connector.connect(user=social.config['USER'], password=social.config['PASS'],
                              host=social.config['HOST'],
                              database=social.config['DB'])

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
        #print(googleAPIResponse)
        #social.logger.debug("signed in: %s", str(googleAPIResponse))
        google_id = googleAPIResponse['id']
        if 'picture' in googleAPIResponse:
            imgurl = googleAPIResponse['picture']
        else:
            imgurl = "/static/images/default_profile.png"
        user_id = get_user(google_id, googleAPIResponse)
        emails = googleAPIResponse['emails']
        email = emails[0]['value']
        #social.logger.debug("user: %s img: %s", user_id, imgurl)
        return Response("ok", mimetype='text/plain')
    except:
       # social.logger.exception("Got an exception")
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

@social.route('/profile')
#######################################################################################
# function : profile
# purpose : renders profile.html
# parameters : None
# returns: profile.html
# Exception : None
#######################################################################################
def profile():
    return render_template("profile.html")

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

@social.route('/updateprofile', methods=['POST'])
#######################################################################################
# function : updateprofile
# purpose : updates user profile in db
# parameters : None
# returns: status
# Exception : None
#######################################################################################
def updateprofile():
    displayname = request.form['displayname']
    gender = request.form['gender']
    organization = request.form['organization']
    user_type = request.form['user_type']
    dateofbirth = request.form['dob']
    User(session['uid']).updateprofile(displayname, gender, organization, user_type, dateofbirth)
    return "User Profile updated"

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
    #social.logger.debug(comment)
    postid =  request.form['postid']
    if comment == "":
        flash('Comment can not be empty')
        redirect(url_for('index'))
    else:
        User(session['uid']).add_comment(comment, postid)
        flash('Your comment has been posted')
    return redirect(url_for('index'))

@social.route('/add_post', methods=['POST'])
#######################################################################################
# function : add_post
# purpose : adds posts newly created by user
# parameters : None
# returns: calls index function
# Exception : None
#######################################################################################
def add_post():
    privacy = request.form['privacy']
    text = request.form['text']
    link = request.form['link']
    if text == "":
            flash('Post can not be empty.')
            redirect(url_for('index'))
    else:
        User(session['uid']).add_post(text, privacy, link)
        flash('Your post has been shared')
    return redirect(url_for('index'))

@social.route('/like_post', methods=['POST'])
#######################################################################################
# function : like_post
# purpose : like posts previously created by user
# parameters : None
# returns: calls index function
# Exception : None
#######################################################################################
def like_post():
    postid = request.form['postid']
    User(session['uid']).like_post(postid)
    flash('You liked the post')
    return redirect(url_for('index'))

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
        GivenName=request.form['givenName']
        familyName=request.form['familyName']
        email = request.form['email']
        user_id = request.form['id']
        user_id = get_user(user_id, email,GivenName,familyName)
        return Response("ok", mimetype='text/plain')
    except:
        #social.logger.exception("Got an exception")
        raise

