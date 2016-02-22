from flask import Flask, request, session, redirect, url_for, render_template, flash, Response, jsonify
from models import User, get_all_recent_posts, get_all_recent_comments, graph
from aqxWeb.sc import app
import mysql.connector
import requests
import aqxdb
from mysql.connector import errorcode
from mysql.connector import connect
###################

def dbconn():
    return mysql.connector.connect(user=app.config['USER'], password=app.config['PASS'],
                              host=app.config['HOST'],
                              database=app.config['DB'])

@app.route('/')
def index():
    posts = get_all_recent_posts()
    comments = get_all_recent_comments()
    return render_template('home.html', posts=posts, comments=comments)

@app.route('/login')
def login():
    return render_template('login.html')

@app.route('/Home')
def home():
    return render_template('userData.html')

@app.route('/signin', methods=['POST'])
def signin():
    try:
        access_token = request.form['access_token']
        print(access_token)
        r = requests.get('https://www.googleapis.com/plus/v1/people/me?access_token='+access_token)
        context = r.json()
        print(context)
        app.logger.debug("signed in: %s", str(context))
        Name=context['name']
        GivenName=Name['givenName']
        familyName=Name['familyName']
        print(GivenName)
        print(familyName)
        emails = context['emails']
        user_id = context['id']
        email=emails[0]['value']
        session['email'] = email

        session['username']= GivenName
        if 'picture' in context:
            imgurl = context['picture']
        else:
            imgurl = "/static/images/default_profile.png"
        user_id = get_user(user_id, email,GivenName,familyName)
        session['uid']=user_id
        print(session['username'])
        app.logger.debug("user: %s img: %s", user_id, imgurl)
        return Response("ok", mimetype='text/plain')
    except:
        app.logger.exception("Got an exception")
        raise
def get_user(google_id, email,GivenName,familyName):
    conn = dbconn()
    cursor = conn.cursor()
    try:
        userID= aqxdb.get_or_create_user(conn, cursor, google_id, email,GivenName,familyName)
        return userID
    finally:
        conn.close()
    print(userID);

@app.route('/profile')
def profile():
    return render_template("profile.html")

@app.route('/editprofile')
def editprofile():
    return render_template("editProfile.html")

@app.route('/updateprofile', methods=['GET', 'POST'])
def updateprofile():
    if request.method == 'POST':
        #firstname = request.form['firstname']
        #lastname = request.form['lastname']
        dateofbirth = request.form['dob']
        displayname = request.form['displayname']
        organization = request.form['organization']
        email = request.form['email']

        User(session['username']).updateprofile(displayname, email, organization)
        return "User Profile updated"

@app.route('/add_comment', methods=['POST'])
def add_comment():
    comment = request.form['newcomment']
    app.logger.debug(comment)
    postid =  request.form['postid']
    if comment == "":
        flash('Comment can not be empty')
        redirect(url_for('index'))
    else:
        User(session['username']).add_comment(comment, postid)
        flash('Your comment has been posted')
    return redirect(url_for('index'))

@app.route('/add_post', methods=['POST'])
def add_post():
    privacy = request.form['privacy']
    text = request.form['text']
    link = request.form['link']
    if text == "":
            flash('Post can not be empty.')
            redirect(url_for('index'))
    else:
        User(session['username']).add_post(text, privacy, link)
        flash('Your post has been shared')
    return redirect(url_for('index'))

@app.route('/like_post', methods=['POST'])
def like_post():
    postid = request.form['postid']
    User(session['username']).like_post(postid)
    flash('You liked the post')
    return redirect(url_for('index'))

@app.route('/logout')
def logout():
    session.pop('username', None)
    flash('Logged out.')
    return redirect(url_for('index'))