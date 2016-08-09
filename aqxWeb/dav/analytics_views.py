import json
import traceback
from flask import Blueprint, render_template, request, redirect, url_for, abort

from app.dav_api import DavAPI
from aqxWeb.app.APIv2 import API as UIAPI

dav = Blueprint('dav', __name__, template_folder='templates', static_folder='static')

app = None

PRE_ESTABLISHED = 100
ESTABLISHED = 200
DEFAULT_MEASUREMENTS_LIST = [6, 7, 2, 1, 9, 8, 10]


######################################################################
# Displays an error page when an error occurs
######################################################################
@dav.route('/error')
def error():
    return render_template("error.html")


def init_dav(flask_app):
    global app
    app = flask_app


######################################################################
# Interactive map of all systems
######################################################################
@dav.route('/explore')
def explore():
    try:
        systems_and_info_json = get_all_systems_info()
        if 'error' in systems_and_info_json:
            print systems_and_info_json['error']
            print("Error processing API call for aquaponic systems data.")
            return render_template("error.html"), 400

        systems = json_loads_byteified(systems_and_info_json)['systems']

        metadata_json = get_all_aqx_metadata()
        if 'error' in metadata_json:
            print metadata_json['error']
            print("Error processing API call for system metadata.")
            return render_template("error.html"), 400

        metadata_dict = json_loads_byteified(metadata_json)['filters']

        return render_template("explore.html", **locals())

    except:
        traceback.print_exc()
        return render_template("error.html"), 400


#######################################################################################
# function : index
# purpose : placeholder for dav.index
# parameters : None
# returns: Index string... no purpose
#######################################################################################
@dav.route('/')
def index():
    return 'Index'


######################################################################
# Interactive graph analysis of system measurements
######################################################################

@dav.route('/analyzeGraph', methods=['POST'])
def analyze_graph():
    try:
        ui_api = UIAPI(app)
        annotations_map = ui_api.getReadableAnnotations()

        # Load JSON formatted String from API.
        # This will be piped into Javascript as a JS Object accessible in that scope
        measurement_types_and_info = get_all_measurement_info()
        if 'error' in measurement_types_and_info:
            print measurement_types_and_info['error']
            print("Error processing API call for measurement types.")
            return render_template("error.html"), 400

        # Load JSON into Python dict with only Byte values, for use in populating dropdowns
        measurement_types = json_loads_byteified(measurement_types_and_info)['measurement_info']
        measurement_names = measurement_types.keys()
        measurement_names.sort()

        selected_systemID_list = []
        try:
            selected_systemID_list = json.dumps(request.form.get('selectedSystems')).translate(None, '\"\\').split(",")

        except:
            traceback.print_exc()
            if not selected_systemID_list:
                print("System ID list or Status is undefined.")
                print("Error processing selected systems form.")
                return render_template("error.html"), 400

        systems_and_measurements_json_pre_est = json_loads_byteified(get_readings_for_tsplot(selected_systemID_list,
                                                                                             DEFAULT_MEASUREMENTS_LIST,
                                                                                             PRE_ESTABLISHED))['response']
        # adding status 100 (pre-established) in every measurement of a system
        for system in systems_and_measurements_json_pre_est:
            for measurement in system['measurement']:
                measurement['status'] = '100'

        if 'error' in systems_and_measurements_json_pre_est:
            print systems_and_measurements_json_pre_est['error']
            print("Error processing API call for measurement readings.")
            return render_template("error.html"), 400

        systems_and_measurements_json = json_loads_byteified(get_readings_for_tsplot(selected_systemID_list,
                                                                                     DEFAULT_MEASUREMENTS_LIST,
                                                                                     ESTABLISHED))['response']
        # adding status 200 (established) in every measurement of a system
        for system in systems_and_measurements_json:
            for measurement in system['measurement']:
                measurement['status'] = '200'

        if 'error' in systems_and_measurements_json:
            print systems_and_measurements_json['error']
            print("Error processing API call for measurement readings.")
            return render_template("error.html"), 400

        # appends measurements of both types to the system_and_measurement_json
        for i in range(len(systems_and_measurements_json)):
            systems_and_measurements_json[i]['measurement'] += systems_and_measurements_json_pre_est[i]['measurement']

        return render_template("analyze.html", **locals())
    except:
        traceback.print_exc()
        return render_template("error.html"), 400


######################################################################
# Interactive graph analysis of a given system measurements
# takes a system_uid as parameter
# displays a graph for the system whose system_uid is given
######################################################################
@dav.route('/analyzeGraph/system/<system_uid>', methods=['GET'])
def system_analyze(system_uid):
    try:
        ui_api = UIAPI(app)
        annotations_map = ui_api.getReadableAnnotations()
        metadata = json.loads(ui_api.getSystem(system_uid))

        # Load JSON formatted String from API.
        # This will be piped into Javascript as a JS Object accessible in that scope
        measurement_types_and_info = get_all_measurement_info()
        if 'error' in measurement_types_and_info:
            print measurement_types_and_info['error']
            print ("Error processing API call for measurement types.")
            return render_template("error.html"), 400

        # Load JSON into Python dict with only Byte values, for use in populating dropdowns
        measurement_types = json_loads_byteified(measurement_types_and_info)['measurement_info']
        measurement_names = measurement_types.keys()
        measurement_names.sort()

        selected_systemID_list = []
        try:
            selected_systemID_list = json.dumps(system_uid).translate(None, '\"\\').split(",")
        except:
            traceback.print_exc()
            if not selected_systemID_list or len(selected_systemID_list) > 1:
                print("Incorrect system ID sent.")
                return render_template("error.html"), 400

        systems_and_measurements_json_pre_est = json_loads_byteified(get_readings_for_tsplot(selected_systemID_list,
                                                                                             DEFAULT_MEASUREMENTS_LIST,
                                                                                             PRE_ESTABLISHED))['response']
        # adding status 200 (established) in every measurement of a system
        for system in systems_and_measurements_json_pre_est:
            for measurement in system['measurement']:
                measurement['status'] = '100'
        if 'error' in systems_and_measurements_json_pre_est:
            print systems_and_measurements_json_pre_est['error']
            return render_template("error.html"), 400

        systems_and_measurements_json = json_loads_byteified(get_readings_for_tsplot(selected_systemID_list,
                                                                                     DEFAULT_MEASUREMENTS_LIST,
                                                                                     ESTABLISHED))['response']
        # adding status 200 (established) in every measurement of a system
        for system in systems_and_measurements_json:
            for measurement in system['measurement']:
                measurement['status'] = '200'

        if 'error' in systems_and_measurements_json:
            print systems_and_measurements_json['error']
            return render_template("error.html"), 400

        # appends measurements of both types to the system_and_measurement_json
        for i in range(len(systems_and_measurements_json)):
            systems_and_measurements_json[i]['measurement'] += systems_and_measurements_json_pre_est[i]['measurement']

        return render_template("systemAnalyze.html", **locals())

    except:
        traceback.print_exc()
        return render_template("error.html"), 400


######################################################################
# API call to get metadata of all the systems
######################################################################

# get_all_systems_info() - It returns the system information as a JSON
#                          object.
def get_all_systems_info():
    dav_api = DavAPI(app)
    return dav_api.get_all_systems_info()


######################################################################
# API call to get filtering criteria
######################################################################

# get_all_aqx_metadata - It returns all the metadata that are needed
#                        to filter the displayed systems.
def get_all_aqx_metadata():
    dav_api = DavAPI(app)
    return dav_api.get_all_filters_metadata()


######################################################################
# API call to get latest recorded values of all measurements of a
# given system (when only system_uid is given)
# API call to get latest record of a given measurement of a given
# system (when both system_uid and measurement_id is given)
######################################################################

@dav.route('/aqxapi/v1/measurements', methods=['GET'])
def get_system_measurement():
    system_uid = request.args.get('system_uid')
    if system_uid is None or len(system_uid) <= 0:
        error_msg_system = json.dumps({'error': 'Invalid system_uid'})
        return error_msg_system, 400
    measurement_id = request.args.get('measurement_id')
    if measurement_id is None:
        dav_api = DavAPI(app)
        result = dav_api.get_system_measurements(system_uid)
    elif len(measurement_id) <= 0:
        error_msg_measurement = json.dumps({'error': 'Invalid measurement id'})
        return error_msg_measurement, 400
    else:
        dav_api = DavAPI(app)
        result = dav_api.get_system_measurement(system_uid, measurement_id)
    if 'error' in result:
        return result, 400
    else:
        return result


######################################################################
# API call to put a record of a given measurement of a given system
######################################################################

@dav.route('/aqxapi/v1/measurements', methods=['PUT'])
def put_system_measurement():
    dav_api = DavAPI(app)
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


######################################################################
# API to get the readings of the time series plot
# the measurements should be sorted in order of the date (ascending)
######################################################################

def get_readings_for_tsplot(system_uid_list, msr_id_list,status_id):
    dav_api = DavAPI(app)
    return dav_api.get_readings_for_plot(system_uid_list, msr_id_list,status_id)


######################################################################
# API to get the readings of the time series plot
# the measurements should be sorted in order of the date (ascending)
######################################################################
@dav.route('/aqxapi/v1/measurements/plot', methods=['POST'])
def get_readings_for_plot():
    dav_api = DavAPI(app)
    measurements = request.json['measurements']
    systems_uid = request.json['systems']
    status_id = request.json['status']
    return dav_api.get_readings_for_plot(systems_uid, measurements,status_id)


######################################################################
# API to get all measurements for picking axis in graph
######################################################################

def get_all_measurement_names():
    dav_api = DavAPI(app)
    return dav_api.get_all_measurement_names()


######################################################################
# API to get all measurements' information: id, name, units, min and
# max
######################################################################

def get_all_measurement_info():
    dav_api = DavAPI(app)
    return dav_api.get_all_measurement_info()


######################################################################
# Helper functions to parse JSON properly into dicts (with byte Strings)
######################################################################

def json_loads_byteified(json_text):
    return _byteify(
        json.loads(json_text, object_hook=_byteify),
        ignore_dicts=True
    )


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
        return {
            _byteify(key, ignore_dicts=True): _byteify(value, ignore_dicts=True)
            for key, value in data.iteritems()
            }
    # if it's anything else, return it in its original form
    return data
