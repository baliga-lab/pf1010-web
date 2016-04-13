from flask import render_template
from frontend import frontend

from servicesV2 import getEnums

import json


######################################################################
# Views
######################################################################

@frontend.route('/')
def index():
    return render_template('index.html')


@frontend.route('/about')
def about():
    return render_template('about.html')


@frontend.route('/resources')
def resources():
    return render_template('resources.html')


@frontend.route('/curriculum')
def curriculum():
    return render_template('curriculum.html')


@frontend.route('/contact')
def contact():
    return render_template('contact.html')


@frontend.route('/system/<system_uid>')
def system(system_uid):
    return render_template('system.html')


@frontend.route('/create_system_page')
def create_system_page():
    enums = json.loads(getEnums())
    return render_template('create_system.html', **locals())


@frontend.route('/badges')
def badges():
    return render_template('badges.html')