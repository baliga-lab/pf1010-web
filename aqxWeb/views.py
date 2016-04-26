from flask import render_template
from frontend import frontend

from servicesV2 import getEnums, getSystem, getLatestReadingsForSystem

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


@frontend.route('/system/<system_uid>/overview')
def sys_overview(system_uid):
    metadata = json.loads(getSystem(system_uid))
    readings = json.loads(getLatestReadingsForSystem(system_uid))
    return render_template('sys_overview.html', **locals())


@frontend.route('/system/<system_uid>/measurements')
def sys_measurements(system_uid):
    metadata = json.loads(getSystem(system_uid))
    readings = json.loads(getLatestReadingsForSystem(system_uid))
    return render_template('sys_measurements.html', **locals())


@frontend.route('/system/<system_uid>/annotations')
def sys_annotations(system_uid):
    metadata = json.loads(getSystem(system_uid))
    return render_template('sys_annotations.html', **locals())


@frontend.route('/create_system_page')
def create_system_page():
    enums = json.loads(getEnums())
    return render_template('create_system.html', **locals())


@frontend.route('/badges')
def badges():
    return render_template('badges.html')