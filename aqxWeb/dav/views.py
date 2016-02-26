from flask import Blueprint, render_template
dav = Blueprint('dav', __name__, template_folder='templates')

@dav.route('/home')
def home():
    return "hi dav"