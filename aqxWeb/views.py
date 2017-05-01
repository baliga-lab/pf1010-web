from flask import render_template, current_app, flash, redirect, url_for, request, session, jsonify
from frontend import frontend
import requests

from aqxWeb.api import API
from aqxWeb.analytics.api import AnalyticsAPI
from aqxWeb.social.models import social_graph
from aqxWeb.social.api import SocialAPI

from aqxWeb.social.models import User, System, Privacy, Group
# put this in a general namespace not in social, damn it !!!
from aqxWeb.social.models import convert_milliseconds_to_normal_date, get_address_from_lat_lng, get_system_measurements_dav_api

import services
import json

BROWSER_NAMES = {
    'msie': 'Internet Explorer', 'chrome': 'Chrome', 'firefox': 'Firefox',
    'safari': 'Safari', 'opera': 'Opera'
}

@frontend.route('/')
def index():
    browser = request.user_agent.browser
    unsupported_browser = False
    if browser in BROWSER_NAMES:
        browser_name = '%s Version %s' % (BROWSER_NAMES[browser], request.user_agent.version)
    else:
        browser_name = 'Unknown Browser'
    if browser != 'chrome' and browser != 'firefox':
        unsupported_browser = True

    return render_template('index.html', **locals())


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
    metadata = json.loads(services.get_system(system_uid))
    readings = json.loads(services.latest_readings_for_system(system_uid))
    user_is_participant = can_user_edit_system(system_uid)
    return render_template('sys_overview.html', **locals())


@frontend.route('/system/<system_uid>/measurements/<measurement>/data')
def sys_data(system_uid, measurement):
    default_page = 1
    dav_api = AnalyticsAPI(current_app)
    metadata = json.loads(services.get_system(system_uid))
    readings = json.loads(dav_api.get_all_data_for_system_and_measurement(system_uid, measurement, default_page))
    measurement_name = measurement.replace('_', ' ')
    return render_template('sys_data.html', **locals())


@frontend.route('/system/<system_uid>/measurements/<measurement>/edit/<created_at>')
def sys_edit_data(system_uid, measurement, created_at):
    dav_api = AnalyticsAPI(current_app)
    metadata = json.loads(services.get_system(system_uid))
    data = json.loads(dav_api.get_measurement_by_created_at(system_uid, measurement, created_at))
    measurement_name = measurement.replace('_', ' ')
    return render_template('edit_data.html', **locals())


def can_user_edit_system(system_uid):
    """
    check user rights for this system: we need to ensure
    that the user is either SYS_PARTICIPANT or SYS_ADMIN
    otherwise redirect to another page.
    """
    if 'uid' in session:
        social_api = SocialAPI(social_graph())
        priv = social_api.user_privilege_for_system(session['uid'], system_uid)
        return priv == 'SYS_ADMIN' or priv == 'SYS_PARTICIPANT'
    return False


@frontend.route('/system/<system_uid>/measurements')
def sys_measurements(system_uid):
    metadata = json.loads(services.get_system(system_uid))
    readings = json.loads(services.latest_readings_for_system(system_uid))
    measurement_types = json.loads(services.measurement_types())
    if can_user_edit_system(system_uid):
        return render_template('sys_measurements.html', **locals())
    else:
        return render_template('no_access.html')


"""
@frontend.route('/system/<system_uid>/annotations')
def sys_annotations(system_uid):
    metadata = json.loads(services.get_system(system_uid))
    if can_user_edit_system(system_uid):
        return render_template('sys_annotations.html', **locals())
    else:
        return render_template('no_access.html')
"""

@frontend.route('/system/<system_uid>/annotations')
def sys_annotations(system_uid):
    api_base_url = current_app.config['CHANGES_API_URL']
    resp = requests.get(api_base_url + '/api/v1.0.0/system_changes/%s/add_base' % system_uid)
    data = json.loads(resp.text)
    return jsonify(data=data)


@frontend.route('/new_system')
def new_system():
    api = API(current_app)
    enums = api.catalogs()
    return render_template('create_system.html', **locals())


@frontend.route('/edit_system/<system_uid>')
def edit_system(system_uid):
    api = API(current_app)
    system_data = api.get_system(system_uid)
    enums = api.catalogs()
    return render_template('edit_system.html', **locals())

@frontend.route('/update_system/<system_uid>', methods=['POST'])
def update_system(system_uid):
    """update_system implements a classic POST-redirect-GET pattern"""
    current_app.logger.info("user id: " + str(session['uid']))
    social_api = SocialAPI(social_graph())
    api = API(current_app)
    system = json.loads(request.form['data'])
    system['UID'] = system_uid
    try:
        priv = social_api.user_privilege_for_system(session['uid'], system_uid)
        if priv == 'SYS_ADMIN':
            api.update_system(system)
            system = api.get_system(system_uid)
            sys_obj = {'system': {
                'system_uid': system['UID'],
                'name': system['name'],
                'description': system['name'],
                'status': system['status']
                }}
            result = social_api.update_system_with_system_uid(sys_obj)
            if "error" in result:
                print result
                flash('could not update social attributes', 'warn')
            else:
                flash('update successful')
        else:
            flash('only administrators can update system attributes')
    except:
        flash('update failed', 'error')

    return redirect(url_for('frontend.edit_system', system_uid=system_uid))


@frontend.route('/system/<system_uid>', methods=['GET'])
def view_system(system_uid):
    user_sql_id = session.get('uid')
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

    privacy_info = Privacy(privacy_options, privacy_default, 'system_social', user_sql_id)
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

    # this is accessing the top level in order to access the system's meta information
    # the actual solution should be to move this view into the top level to
    # have a clear directed dependency
    general_api = API(current_app)
    system_metadata = general_api.get_system(system_uid)
    growbed_media_str = ', '.join([m['name'] for m in  system_metadata['gbMedia']])
    crops_str = ', '.join(['%s (%d)' % (c['name'], c['count'])
                           for c in  system_metadata['crops']])
    aquatic_str = ', '.join(['%s (%d)' % (c['name'], c['count'])
                           for c in  system_metadata['organisms']])
    return render_template("system_view.html", **locals())
