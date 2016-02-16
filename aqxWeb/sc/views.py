from flask import Flask, request, session, redirect, url_for, render_template, flash
from models import User
from aqxWeb.sc import app

@app.route('/')
def index():
    return render_template("index.html")

@app.route('/updateprofile', methods=['GET', 'POST'])
def updateprofile():
    if request.method == 'POST':
        firstname = request.form['firstname']
        lastname = request.form['lastname']
        dateofbirth = request.form['dob']
        organization = request.form['organization']
        email = request.form['email']
        User(firstname, lastname, dateofbirth, organization, email).updateprofile()
        return "User Profile updated"

'''
if __name__ == '__main__':
    app.run(debug=True)
    '''