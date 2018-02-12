from flask import render_template, current_app, flash, redirect, url_for, request, session, jsonify, abort
from werkzeug import secure_filename
from frontend import frontend
import requests
from werkzeug.exceptions import BadRequestKeyError

from aqxWeb.api import API
from aqxWeb.analytics.api import AnalyticsAPI
from aqxWeb.social.models import social_graph
from aqxWeb.social.api import SocialAPI

from aqxWeb.social.models import User, System, Privacy, Group
# put this in a general namespace not in social, damn it !!!
from aqxWeb.social.models import convert_milliseconds_to_normal_date, get_address_from_lat_lng

import aqxWeb.utils as utils

# this is ugly, but: this app currently has too many layers
# of indirection which we need to eliminate for long-term benefit
from aqxWeb.dao.measurements import MeasurementDAO
from aqxWeb.dao.systems import SystemDAO

import services
import json
import traceback
import os
import tempfile
import pandas
import numpy as np
import datetime
import time


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


@frontend.route('/system/<system_uid>/measurements/<measurement>/data')
def sys_data(system_uid, measurement):
    default_page = 1
    dav_api = AnalyticsAPI(current_app)
    metadata = json.loads(services.get_system(system_uid))
    readings = json.loads(dav_api.get_all_data_for_system_and_measurement(system_uid, measurement, default_page))
    measurements = readings['data']
    measurement_dao = MeasurementDAO(current_app)
    measurement_types = {mt['name']: (mt['full_name'], mt['unit'])
                         for mt in measurement_dao.measurement_types()}
    measurement_name = measurement_types[measurement][0]
    measurement_unit = measurement_types[measurement][1]
    return render_template('sys_data.html', **locals())


@frontend.route('/system/<system_uid>/measurements/<measurement>/edit/<created_at>')
def sys_edit_data(system_uid, measurement, created_at):
    dav_api = AnalyticsAPI(current_app)
    metadata = json.loads(services.get_system(system_uid))
    data = json.loads(dav_api.get_measurement_by_created_at(system_uid, measurement, created_at))

    measurement_dao = MeasurementDAO(current_app)
    measurement_types = {mt['name']: (mt['full_name'], mt['unit'])
                         for mt in measurement_dao.measurement_types()}
    measurement_name = measurement_types[measurement][0]
    measurement_unit = measurement_types[measurement][1]
    if measurement_unit == 'celsius':
        measurement_unit = '&deg;C'
    return render_template('edit_data.html', **locals())

def __timestamp_from_time_str(s):
    timestamp_str = 'T'.join(s.split(' ')) + 'Z'
    return utils.get_timestamp(timestamp_str)

@frontend.route('/system/<system_uid>/update-measurement/<measurement>/<time>', methods=['POST'])
def update_measurement(system_uid, measurement, time):
    """Action connected to the measurement form"""
    if not can_user_edit_system(system_uid):
        return render_template('no_access.html')
    value = request.form['value']
    timestamp = __timestamp_from_time_str(time)
    measurement_dao = MeasurementDAO(current_app)
    measurement_dao.update_measurement(system_uid, timestamp, measurement, value)
    # go back to history
    return redirect(url_for('frontend.sys_data', system_uid=system_uid, measurement=measurement))

@frontend.route('/system/<system_uid>/update-measurement/<measurement>/<time>', methods=['DELETE'])
def delete_measurement(system_uid, measurement, time):
    if not can_user_edit_system(system_uid):
        return jsonify(status='error', message='no rights to delete this entry')

    timestamp = __timestamp_from_time_str(time)
    measurement_dao = MeasurementDAO(current_app)
    measurement_dao.delete_measurement(system_uid, timestamp, measurement)
    return jsonify(status='ok')


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


def parse_time(s):
    try:
        # timestamp = time.mktime(tup)
        tup = datetime.datetime.strptime(s, '%Y-%m-%d %H:%M:%S').timetuple()
        return datetime.datetime.fromtimestamp(time.mktime(tup))
    except:
        pass
    try:
        tup = datetime.datetime.strptime(s, '%m/%d/%Y %H:%M:%S').timetuple()
        return datetime.datetime.fromtimestamp(time.mktime(tup))
    except:
        traceback.print_exc()
        return None


def parse_value(s):
    return float(s)


# map to the database prefixes
UPLOAD_MT_MAP = {
    'alkalinity': 'alkalinity', 'ammonium': 'ammonium', 'chlorine': 'chlorine',
    'hardness': 'hardness', 'light': 'light', 'nitrate': 'nitrate',
    'nitrite': 'nitrite', 'oxygen': 'o2', 'ph': 'ph', 'temp': 'temp',
    'leafs': 'leaf_count', 'plant_height': 'height', 'time': 'time'
}


@frontend.route('/system/<system_uid>/upload-measurements', methods=['POST'])
def upload_measurements(system_uid):
    """Action connected to the measurement form"""
    current_app.logger.info("upload_measurements()")
    if not can_user_edit_system(system_uid):
        return render_template('no_access.html')
    try:
        import_file = request.files['importfile']
        measurement_dao = MeasurementDAO(current_app)
        print(import_file)
        with tempfile.TemporaryFile() as outfile:
            import_file.save(outfile)
            outfile.seek(0)
            df = pandas.read_csv(outfile, sep='\t', index_col=None, header=0)
            measurements = []
            for i, row in df.iterrows():
                for col in df.columns:
                    try:
                        prefix = UPLOAD_MT_MAP[col]
                        if prefix == 'time':
                            mtime = parse_time(row[col])
                        else:
                            value = parse_value(row[col])
                            if not np.isnan(value):
                                measurements.append((prefix, value))

                    except KeyError:
                        flash("not found: '%s'" % col, 'error')
                # all columns processed, now store
                if measurements > 0:
                    current_app.logger.info('storing for system %s', system_uid)
                    try:
                        measurement_dao.store_measurements(system_uid, mtime, measurements)
                    except:
                        flash('errors during import, you are likely trying to add values that already exist (%s)' % (str(mtime)), 'error')

        ## standard message
        flash('Uploaded values were stored.')
    except BadRequestKeyError:
        flash('Please provide an upload file', 'error')
    except pandas.io.common.CParserError:
        flash('Please provide a valid tsv file', 'error')
    return redirect(url_for('frontend.view_system', system_uid=system_uid))


@frontend.route('/system/<system_uid>/record-measurements', methods=['POST'])
def record_measurements(system_uid):
    """Action connected to the measurement form"""
    if not can_user_edit_system(system_uid):
        return render_template('no_access.html')

    sys_uid = request.form['system-uid']
    measure_date = request.form['measure-date']
    measure_time = request.form['measure-time']
    mtime = utils.get_form_time(measure_date, measure_time)
    measurement_dao = MeasurementDAO(current_app)
    measurement_types = [mt['name'] for mt in measurement_dao.measurement_types()]
    measurements = []
    for prefix in measurement_types:
        if prefix + '-use' in request.form:
            value = float(request.form[prefix + '-value'])
            measurements.append((prefix, value))
    if measurements > 0:
        measurement_dao.store_measurements(system_uid, mtime, measurements)

    return redirect(url_for('frontend.view_system', system_uid=system_uid))


@frontend.route('/new_system')
def new_system():
    api = API(current_app)
    enums = api.catalogs()
    return render_template('create_system.html', **locals())


@frontend.route('/edit_system/<system_uid>')
def edit_system(system_uid):
    alert_status = request.args.get('status')
    if alert_status is not None:
        if alert_status == 'delete_ok':
            flash('Entry was successfully deleted.', 'success')
        elif alert_status == 'delete_error':
            flash('Entry could not be deleted.', 'danger')
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
                flash('could not update social attributes', 'warning')
            else:
                flash('update successful', 'success')
        else:
            flash('only administrators can update system attributes', 'danger')
    except:
        flash('update failed', 'danger')

    return redirect(url_for('frontend.edit_system', system_uid=system_uid))


@frontend.route('/<system_uid>/crop/<crop_id>', methods=['DELETE'])
def delete_crop(system_uid, crop_id):
    if can_user_edit_system(system_uid):
        system_dao = SystemDAO(current_app)
        try:
            system_dao.delete_crop_from_system(system_uid, crop_id)
            return jsonify(status='ok')
        except:
            return jsonify(status='error')
    else:
        return jsonify(status='error')


@frontend.route('/<system_uid>/organism/<organism_id>', methods=['DELETE'])
def delete_organism(system_uid, organism_id):
    if can_user_edit_system(system_uid):
        system_dao = SystemDAO(current_app)
        try:
            system_dao.delete_organism_from_system(system_uid, organism_id)
            return jsonify(status='ok')
        except:
            return jsonify(status='error')
    else:
        return jsonify(status='error')


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

    dav_api = AnalyticsAPI(current_app)
    json_output_measurement = dav_api.get_system_measurements(system_uid)
    latest_measurements = None
    if "error" not in json_output_measurement:
        latest_measurements = json_output_measurement['measurements']

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

    strip_measurement_types = ['alkalinity', 'ammonium', 'chlorine', 'hardness', 'nitrate', 'nitrite', 'ph']
    measurement_dao = MeasurementDAO(current_app)
    all_measurement_types = [mt['name'] for mt in measurement_dao.measurement_types()]
    img_url = image_url(system_uid)
    return render_template("system_view.html", **locals())


@frontend.route('/subscribe-updates', methods=['POST'])
def subscribe_updates():
    email = request.form['email'].strip()
    api = API(current_app)
    if len(email) == 0:
        return jsonify(status='error', message="Please provide a valid email address")
    else:
        try:
            result = api.subscribe(email)
            return jsonify(status=result['status'], message="Successfully subscribed")
        except:
            return jsonify(status='error', message="Error while trying to subscribe")


@frontend.route("/details_image_placeholder/<system_uid>", methods=["GET"])
def details_images_placeholder(system_uid):
    """a simple snippet to add an image control"""
    user_sql_id = session.get('uid')
    img_url = request.args.get('img_url');
    user_privilege = System().get_user_privilege_for_system(user_sql_id, system_uid)
    return render_template('details_image_placeholder.html', **locals())


@frontend.route("/details_image_div/<system_uid>", methods=["GET"])
def details_images_div(system_uid):
    """a simple snippet to add an image control"""
    user_sql_id = session.get('uid')
    img_url = request.args.get('img_url');
    user_privilege = System().get_user_privilege_for_system(user_sql_id, system_uid)
    return render_template('details_image_div.html', **locals())

@frontend.route('/clear-system-image/<system_uid>', methods=['DELETE'])
def clear_system_image(system_uid):
    if can_user_edit_system(system_uid):
        filename = "%s.jpg" % system_uid
        thumb_name = "%s_thumb.jpg" % system_uid
        target_path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
        thumb_path = os.path.join(current_app.config['UPLOAD_FOLDER'], thumb_name)
        if os.path.exists(target_path):
            os.remove(target_path)
            if os.path.exists(thumb_path):
                os.remove(thumb_path)
        else:
            filename = "%s.png" % system_uid
            thumb_name = "%s_thumb.png" % system_uid
            target_path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
            thumb_path = os.path.join(current_app.config['UPLOAD_FOLDER'], thumb_name)
            if os.path.exists(target_path):
                os.remove(target_path)
                if os.path.exists(thumb_path):
                    os.remove(thumb_path)

        return jsonify(status="ok")
    else:
        return jsonify(error="attempt to modify non-owned system")


@frontend.route("/system_image", methods=["POST"])
def set_system_image():
    sys_uid = request.form['system-uid']
    if can_user_edit_system(sys_uid):
        file = request.files['image-file']
        if file:
            filename = secure_filename(file.filename)
            suffix = filename.split('.')[-1].lower()
            current_app.logger.debug('suffix: %s', suffix)
            if suffix in {'png', 'jpg'}:
                filename = "%s.%s" % (sys_uid, suffix)
                target_path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
                current_app.logger.info('upload file: %s', target_path)
                file.save(target_path)
                utils.make_thumbnail(current_app.config['UPLOAD_FOLDER'],
                                           sys_uid, overwrite=True)
                return jsonify(status="Ok", img_url="/static/uploads/%s" % filename)
            else:
                return jsonify(error="invalid image file name")
        else:
            return jsonify(error="please specify an image file")
    else:
        return jsonify(error="unauthorized attempt to set image file")


#### HELPERS #####

def image_url(system_uid):
    img_url = None
    mtime = None
    jpg_path = os.path.join(current_app.config['UPLOAD_FOLDER'], "%s.jpg" % system_uid)
    if os.path.exists(jpg_path):
        mtime = os.path.getmtime(jpg_path)
        img_url = '/static/uploads/%s.jpg?%s' % (system_uid, str(mtime))
    if img_url is None:
        png_path = os.path.join(current_app.config['UPLOAD_FOLDER'], "%s.png" % system_uid)
        if os.path.exists(png_path):
            mtime = os.path.getmtime(png_path)
            img_url = '/static/uploads/%s.png?%s' % (system_uid, str(mtime))
    return img_url
