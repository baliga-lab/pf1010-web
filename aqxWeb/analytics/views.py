import json
import traceback
import time
from flask import Blueprint, render_template, request, current_app, session

from aqxWeb.social.models import social_graph
from aqxWeb.social.api import SocialAPI
from aqxWeb.analytics.api import AnalyticsAPI

# TODO: seems like a cyclic module dependency to me, can we break it ?
from aqxWeb.api import API as UIAPI

dav = Blueprint('dav', __name__, template_folder='templates', static_folder='static')

PRE_ESTABLISHED = 100
ESTABLISHED = 200
DEFAULT_MEASUREMENTS_LIST = [6, 7, 2, 1, 9, 8, 10]


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


@dav.route('/error')
def error():
    return render_template("error.html")


@dav.route('/explore')
def explore():
    try:
        systems_and_info_json = get_all_systems_info()
        if 'error' in systems_and_info_json:
            current_app.logger.info(systems_and_info_json['error'])
            current_app.logger.info("Error processing API call for aquaponic systems data.")
            return render_template("error.html"), 400

        systems = json_loads_byteified(systems_and_info_json)['systems']

        metadata_json = get_all_aqx_metadata()
        if 'error' in metadata_json:
            current_app.logger.info(metadata_json['error'])
            current_app.logger.info("Error processing API call for system metadata.")
            return render_template("error.html"), 400

        metadata_dict = json_loads_byteified(metadata_json)['filters']

        return render_template("explore.html", **locals())

    except:
        traceback.print_exc()
        return render_template("error.html"), 400


@dav.route('/')
def index():
    return 'Index'


@dav.route('/analyzeGraph', methods=['POST'])
def analyze_graph():
    """This analyze page is coming from the Explore page"""
    current_app.logger.info('analyze_graph()')
    try:
        ui_api = UIAPI(current_app)
        annotations_map = ui_api.getReadableAnnotations()

        # Load JSON formatted String from API.
        # This will be piped into Javascript as a JS Object accessible in that scope
        measurement_types_and_info = __get_all_measurement_info()
        if 'error' in measurement_types_and_info:
            current_app.logger(measurement_types_and_info['error'])
            current_app.logger("Error processing API call for measurement types.")
            return render_template("error.html"), 400
        measurement_types_and_info_json = json.dumps(measurement_types_and_info)

        measurement_types = measurement_types_and_info['measurement_info']
        measurement_names = measurement_types.keys()
        measurement_names.sort()

        selected_systemID_list = []
        try:
            selected_systemID_list = json.dumps(request.form.get('selectedSystems')).translate(None, '\"\\').split(",")

        except:
            traceback.print_exc()
            if not selected_systemID_list:
                current_app.logger.info("System ID list or Status is undefined.")
                current_app.logger.info("Error processing selected systems form.")
                return render_template("error.html"), 400

        systems_and_measurements_json_pre_est = json_loads_byteified(get_readings_for_tsplot(selected_systemID_list,
                                                                                             DEFAULT_MEASUREMENTS_LIST,
                                                                                             PRE_ESTABLISHED))['response']
        # adding status 100 (pre-established) in every measurement of a system
        for system in systems_and_measurements_json_pre_est:
            for measurement in system['measurement']:
                measurement['status'] = '100'

        if 'error' in systems_and_measurements_json_pre_est:
            current_app.logger.info(systems_and_measurements_json_pre_est['error'])
            current_app.logger.info("Error processing API call for measurement readings.")
            return render_template("error.html"), 400

        systems_and_measurements_json = json_loads_byteified(get_readings_for_tsplot(selected_systemID_list,
                                                                                     DEFAULT_MEASUREMENTS_LIST,
                                                                                     ESTABLISHED))['response']
        # adding status 200 (established) in every measurement of a system
        for system in systems_and_measurements_json:
            for measurement in system['measurement']:
                measurement['status'] = '200'

        if 'error' in systems_and_measurements_json:
            current_app.logger.info(systems_and_measurements_json['error'])
            current_app.logger.info("Error processing API call for measurement readings.")
            return render_template("error.html"), 400

        # appends measurements of both types to the system_and_measurement_json
        for i in range(len(systems_and_measurements_json)):
            systems_and_measurements_json[i]['measurement'] += systems_and_measurements_json_pre_est[i]['measurement']

        return render_template("analyze.html", **locals())
    except:
        traceback.print_exc()
        return render_template("error.html"), 400


@dav.route('/analyzeGraph/system/<system_uid>', methods=['GET'])
def system_analyze(system_uid):
    """This route is for analyzing coming from a system's info page"""
    try:
        ui_api = UIAPI(current_app)
        annotations_map = ui_api.getReadableAnnotations()
        metadata = ui_api.get_system(system_uid)
        user_is_participant = can_user_edit_system(system_uid)

        # Load JSON formatted String from API.
        # This will be piped into Javascript as a JS Object accessible in that scope
        measurement_types_and_info = __get_all_measurement_info()
        if 'error' in measurement_types_and_info:
            current_app.logger.info(measurement_types_and_info['error'])
            current_app.logger.info("Error processing API call for measurement types.")
            return render_template("error.html"), 400
        measurement_types_and_info_json = json.dumps(measurement_types_and_info)
        measurement_types = measurement_types_and_info['measurement_info']
        measurement_names = measurement_types.keys()
        measurement_names.sort()

        selected_systemID_list = []
        try:
            selected_systemID_list = json.dumps(system_uid).translate(None, '\"\\').split(",")
        except:
            traceback.print_exc()
            if not selected_systemID_list or len(selected_systemID_list) > 1:
                current_app.logger.info("Incorrect system ID sent.")
                return render_template("error.html"), 400

        systems_and_measurements_json_pre_est = json_loads_byteified(get_readings_for_tsplot(selected_systemID_list,
                                                                                             DEFAULT_MEASUREMENTS_LIST,
                                                                                             PRE_ESTABLISHED))['response']
        # adding status 200 (established) in every measurement of a system
        for system in systems_and_measurements_json_pre_est:
            for measurement in system['measurement']:
                measurement['status'] = '100'
        if 'error' in systems_and_measurements_json_pre_est:
            current_app.logger.info(systems_and_measurements_json_pre_est['error'])
            return render_template("error.html"), 400

        systems_and_measurements_json = json_loads_byteified(get_readings_for_tsplot(selected_systemID_list,
                                                                                     DEFAULT_MEASUREMENTS_LIST,
                                                                                     ESTABLISHED))['response']
        # adding status 200 (established) in every measurement of a system
        for system in systems_and_measurements_json:
            for measurement in system['measurement']:
                measurement['status'] = '200'

        if 'error' in systems_and_measurements_json:
            current_app.logger.info(systems_and_measurements_json['error'])
            return render_template("error.html"), 400

        # appends measurements of both types to the system_and_measurement_json
        for i in range(len(systems_and_measurements_json)):
            systems_and_measurements_json[i]['measurement'] += systems_and_measurements_json_pre_est[i]['measurement']

        return render_template("systemAnalyze.html", **locals())

    except:
        traceback.print_exc()
        return render_template("error.html"), 400


def get_all_systems_info():
    """returns system inforamtion as JSON"""
    dav_api = AnalyticsAPI(current_app)
    return dav_api.get_all_systems_info()


def get_all_aqx_metadata():
    dav_api = AnalyticsAPI(current_app)
    return dav_api.get_all_filters_metadata()


@dav.route('/aqxapi/v1/measurements', methods=['GET'])
def get_system_measurement():
    system_uid = request.args.get('system_uid')
    if system_uid is None or len(system_uid) <= 0:
        error_msg_system = json.dumps({'error': 'Invalid system_uid'})
        return error_msg_system, 400
    measurement_id = request.args.get('measurement_id')
    if measurement_id is None:
        dav_api = AnalyticsAPI(current_app)
        result = dav_api.get_system_measurements(system_uid)
    elif len(measurement_id) <= 0:
        error_msg_measurement = json.dumps({'error': 'Invalid measurement id'})
        return error_msg_measurement, 400
    else:
        dav_api = AnalyticsAPI(current_app)
        result = dav_api.get_system_measurement(system_uid, measurement_id)
    if 'error' in result:
        return result, 400
    else:
        return result


@dav.route('/aqxapi/v1/measurements', methods=['PUT'])
def put_system_measurement():
    dav_api = AnalyticsAPI(current_app)
    data = request.get_json()
    system_uid = data.get('system_uid')
    if system_uid is None or len(system_uid) <= 0:
        error_msg_system = json.dumps({'error': 'System_uid required'})
        return error_msg_system, 400
    measurement_id = data.get('measurement_id')
    if measurement_id is None or len(measurement_id) <= 0:
        error_msg_measurement = json.dumps({'error': 'Measurement id required'})
        return error_msg_measurement, 400
    time = data.get('time')
    if time is None or len(time) <= 0:
        error_msg_time = json.dumps({'error': 'Time required'})
        return error_msg_time, 400
    value = data.get('value')
    if value is None:
        error_msg_value = json.dumps({'error': 'Value required'})
        return error_msg_value, 400
    min = data.get('min')
    max = data.get('max')
    if value < min or value > max:
        error_msg_flow = json.dumps({'error': 'Value too high or too low'})
        return error_msg_flow, 400
    else:
        result = dav_api.put_system_measurement(system_uid, measurement_id, time, value)
    if 'error' in result:
        return result, 400
    else:
        return result, 201


def get_readings_for_tsplot(system_uid_list, msr_id_list,status_id):
    dav_api = AnalyticsAPI(current_app)
    return dav_api.get_readings_for_plot(system_uid_list, msr_id_list,status_id)


@dav.route('/aqxapi/v1/measurements/plot', methods=['POST'])
def get_readings_for_plot():
    dav_api = AnalyticsAPI(current_app)
    measurements = request.json['measurements']
    systems_uid = request.json['systems']
    status_id = request.json['status']
    return dav_api.get_readings_for_plot(systems_uid, measurements,status_id)

@dav.route('/aqxapi/measurements/<measurement_id>/system/<system_uid>/<page>', methods=['GET'])
def get_all_for_system_and_measurement(system_uid, measurement_id, page):
    dav_api = AnalyticsAPI(current_app)
    measurements = dav_api.get_all_data_for_system_and_measurement(system_uid, measurement_id, page)
    if 'error' in measurements:
        return measurements, 400
    if '[]' in measurements:
        return measurements, 204
    return measurements, 200


@dav.route('/aqxapi/v1/measurements/update', methods=['PUT'])
def edit_measurement_for_system():
    dav_api = AnalyticsAPI(current_app)
    measurement = request.json
    if time.strptime(measurement['time'], '%Y-%m-%d %H:%M:%S') >= time.strptime(measurement['updated_at'], '%Y-%m-%d %H:%M:%S'):
        return json.dumps({'error': 'Invalid update time. The update time must come after the original measurement time.'}), 400
    if 'error' in dav_api.get_measurement_by_created_at(measurement['system_uid'], measurement['measurement_name'], measurement['time']):
        error_not_found = json.dumps({'error': 'Cannot update measurement. Measurement not found.'})
        return error_not_found, 404
    return dav_api.edit_measurement(measurement['system_uid'], measurement['measurement_name'], measurement)


def get_all_measurement_names():
    dav_api = AnalyticsAPI(current_app)
    return dav_api.get_all_measurement_names()


def __get_all_measurement_info():
    """returns a dictionary of the form {'measurement_info': {<measurement_name>: {<infos>}, ...}}"""
    dav_api = AnalyticsAPI(current_app)
    return dav_api.get_all_measurement_info()


def json_loads_byteified(json_text):
    return _byteify(json.loads(json_text, object_hook=_byteify),
                    ignore_dicts=True)


def _byteify(data, ignore_dicts=False):
    # if this is a unicode string, return its string representation
    if isinstance(data, unicode):
        return data.encode('utf-8')

    # if this is a list of values, return list of byteified values
    if isinstance(data, list):
        return [_byteify(item, ignore_dicts=True) for item in data]

    # if this is a dictionary, return dictionary of byteified keys and values
    # but only if we haven't already byteified it
    if isinstance(data, dict) and not ignore_dicts:
        return { _byteify(key, ignore_dicts=True): _byteify(value, ignore_dicts=True)
                 for key, value in data.iteritems() }

    # if it's anything else, return it in its original form
    return data
