from flask import render_template, current_app
from frontend import frontend
from aqxWeb.api import API
from aqxWeb.analytics.api import AnalyticsAPI

import services

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
    metadata = json.loads(services.getSystem(system_uid))
    readings = json.loads(services.latest_readings_for_system(system_uid))
    return render_template('sys_overview.html', **locals())


@frontend.route('/system/<system_uid>/measurements/<measurement>/data')
def sys_data(system_uid, measurement):
    default_page = 1
    dav_api = AnalyticsAPI(current_app)
    metadata = json.loads(services.getSystem(system_uid))
    readings = json.loads(dav_api.get_all_data_for_system_and_measurement(system_uid, measurement, default_page))
    measurement_name = measurement.replace('_', ' ')
    return render_template('sys_data.html', **locals())


@frontend.route('/system/<system_uid>/measurements/<measurement>/edit/<created_at>')
def sys_edit_data(system_uid, measurement, created_at):
    dav_api = AnalyticsAPI(current_app)
    metadata = json.loads(services.getSystem(system_uid))
    data = json.loads(dav_api.get_measurement_by_created_at(system_uid, measurement, created_at))
    measurement_name = measurement.replace('_', ' ')
    return render_template('edit_data.html', **locals())


@frontend.route('/system/<system_uid>/measurements')
def sys_measurements(system_uid):
    metadata = json.loads(services.getSystem(system_uid))
    readings = json.loads(services.latest_readings_for_system(system_uid))
    measurement_types = json.loads(services.measurement_types())

    return render_template('sys_measurements.html', **locals())


@frontend.route('/system/<system_uid>/annotations')
def sys_annotations(system_uid):
    metadata = json.loads(services.getSystem(system_uid))
    return render_template('sys_annotations.html', **locals())


@frontend.route('/new_system')
def new_system():
    api = API(current_app)
    enums = api.catalogs()
    return render_template('create_system.html', **locals())


@frontend.route('/edit_system/<system_uid>')
def edit_system(system_uid):
    api = API(current_app)
    system_data = api.getSystem(system_uid)
    enums = api.catalogs()
    return render_template('edit_system.html', **locals())


@frontend.route('/badges')
def badges():
    return render_template('badges.html')
