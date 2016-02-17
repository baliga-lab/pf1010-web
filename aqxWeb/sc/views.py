from flask import Flask, request, session, redirect, url_for, render_template, flash
from models import User,get_todays_recent_posts
from aqxWeb.sc import app

@app.route('/profile')
def profile():
    return render_template("profile.html")

@app.route('/updateprofile', methods=['GET', 'POST'])
def updateprofile():
    if request.method == 'POST':
        firstname = request.form['firstname']
        lastname = request.form['lastname']
        dateofbirth = request.form['dob']
        organization = request.form['organization']
        email = request.form['email']

        User(session['username']).updateprofile(firstname, lastname, dateofbirth, organization, email)
        return "User Profile updated"

@app.route('/')
def index():
    posts = get_todays_recent_posts()
    return render_template('home.html', posts=posts)

@app.route('/add_post', methods=['POST'])
def add_post():
    title = request.form['title']
    tags = request.form['tags']
    text = request.form['text']

    if not title or not tags  or not text:
        if not title:
            flash('You must give your post a title.')
        if not tags:
            flash('You must give your post at least one tag.')
        if not text:
            flash('You must give your post a text body.')
    else:
        User(session['username']).add_post(title,tags, text)

    return redirect(url_for('index'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        if not User(username).verify_password(password):
            flash('Invalid login.')
        else:
            session['username'] = username
            flash('Logged in.')
            return redirect(url_for('index'))

    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('username', None)
    flash('Logged out.')
    return redirect(url_for('index'))