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
        dav_api = AnalyticsAPI(current_app)
        systems_and_info = dav_api.get_all_systems_info()
        systems_and_info_json = json.dumps(systems_and_info);
        filters_metadata = dav_api.get_all_filters_metadata()
        metadata_dict = filters_metadata['filters']

        return render_template("explore.html", **locals())

    except:
        traceback.print_exc()
        return render_template("error.html"), 400


@dav.route('/analyzeGraph', methods=['POST'])
def analyze_graph():
    """This analyze page is coming from the Explore page"""
    current_app.logger.info('analyze_graph()')
    try:
        ui_api = UIAPI(current_app)

        # Load JSON formatted String from API.
        # This will be piped into Javascript as a JS Object accessible in that scope
        measurement_types_and_info = __get_all_measurement_info()
        if 'error' in measurement_types_and_info:
            current_app.logger(measurement_types_and_info['error'])
            raise Exception("Error processing API call for measurement types.")

        measurement_types_and_info_json = json.dumps(measurement_types_and_info)
        measurement_types = sorted(measurement_types_and_info['measurement_info'].keys())
        selected_systemIDs = map(lambda s: s.encode('ascii'), request.form.get('selectedSystems').strip("\"").split(','))
        systems_and_measurements = json.dumps(__get_systems_and_measurements(selected_systemIDs))

        return render_template("analyze.html", **locals())
    except:
        traceback.print_exc()
        return render_template("error.html"), 400


def __get_systems_and_measurements(system_uids):
    systems_and_measurements_pre_est = get_readings_for_tsplot(system_uids, DEFAULT_MEASUREMENTS_LIST,
                                                               PRE_ESTABLISHED)['response']

    if 'error' in systems_and_measurements_pre_est:
        current_app.logger.info(systems_and_measurements_pre_est['error'])
        raise Exception('Error in retrieving measurements')

    # adding status 200 (established) in every measurement of a system
    for system in systems_and_measurements_pre_est:
        for measurement in system['measurement']:
            measurement['status'] = '100'

    systems_and_measurements = get_readings_for_tsplot(system_uids, DEFAULT_MEASUREMENTS_LIST,
                                                       ESTABLISHED)['response']

    if 'error' in systems_and_measurements:
        current_app.logger.info(systems_and_measurements['error'])
        raise Exception('Error in retrieving measurements')

    # adding status 200 (established) in every measurement of a system
    for system in systems_and_measurements:
        for measurement in system['measurement']:
            measurement['status'] = '200'

    # appends measurements of both types to the system_and_measurement_json
    for i in range(len(systems_and_measurements)):
        systems_and_measurements[i]['measurement'] += systems_and_measurements_pre_est[i]['measurement']

    return systems_and_measurements


@dav.route('/analyzeGraph/<system_uid>', methods=['GET'])
def system_analyze(system_uid):
    """This route is for analyzing coming from a system's info page"""
    try:
        ui_api = UIAPI(current_app)
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
        measurement_types = sorted(measurement_types_and_info['measurement_info'].keys())
        systems_and_measurements = json.dumps(__get_systems_and_measurements([system_uid]))

        return render_template("systemAnalyze.html", **locals())

    except:
        traceback.print_exc()
        return render_template("error.html"), 400

def get_readings_for_tsplot(system_uid_list, msr_id_list,status_id):
    dav_api = AnalyticsAPI(current_app)
    return dav_api.get_readings_for_plot(system_uid_list, msr_id_list,status_id)


@dav.route('/aqxapi/v1/measurements/plot', methods=['POST'])
def get_readings_for_plot():
    """This API is called by the graph Javascript for dynamic updating"""
    dav_api = AnalyticsAPI(current_app)
    measurements = request.json['measurements']
    systems_uid = request.json['systems']
    status_id = request.json['status']
    return json.dumps(dav_api.get_readings_for_plot(systems_uid, measurements,status_id))


def get_all_measurement_names():
    return AnalyticsAPI(current_app).get_all_measurement_names()


def __get_all_measurement_info():
    """returns a dictionary of the form {'measurement_info': {<measurement_name>: {<infos>}, ...}}"""
    dav_api = AnalyticsAPI(current_app)
    return dav_api.get_all_measurement_info()
