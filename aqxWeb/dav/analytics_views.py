import json
import traceback
from flask import Blueprint, render_template, request, redirect, url_for, abort

from app.dav_api import DavAPI

dav = Blueprint('dav', __name__, template_folder='templates', static_folder='static')

pool = None


@dav.route('/home')
def home():
    return "Data Analytics and Viz Homepage"


def init_dav(conn_pool):
    global pool
    pool = conn_pool


######################################################################
# method to get db connection from pool
######################################################################

def get_conn():
    return pool.get_connection()


######################################################################
# Interactive map of all active systems
######################################################################
@dav.route('/explore')
def explore():
    systems_and_info_json = get_all_systems_info()
    if 'error' in systems_and_info_json:
        raise AttributeError("Error processing API call for aquaponic systems data.")

    systems = json_loads_byteified(systems_and_info_json)['systems']

    metadata_json = get_all_aqx_metadata()
    if 'error' in metadata_json:
        raise AttributeError("Error processing API call for system metadata.")

    metadata_dict = json_loads_byteified(metadata_json)['filters']

    return render_template("explore.html", **locals())


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
    msr_id_list = [6, 7, 2, 1, 9, 8, 10]

    # Load JSON formatted String from API. This will be piped into Javascript as a JS Object accessible in that scope
    # TODO: There are currently no error pages, we're just stubbing abort for now
    measurement_types_and_info = get_all_measurement_info()
    if 'error' in measurement_types_and_info:
        raise AttributeError("Error processing API call for measurement types.")

    # Load JSON into Python dict with only Byte values, for use in populating dropdowns
    measurement_types = json_loads_byteified(measurement_types_and_info)['measurement_info']
    measurement_names = measurement_types.keys()
    measurement_names.sort()

    selected_systemID_list = []
    try:
        selected_systemID_list = json.dumps(request.form.get('selectedSystems')).translate(None, '\"\\').split(",")
    except:
        if 'error' in selected_systemID_list:
            raise AttributeError("Error processing API call for system IDs.")
        else:
            traceback.print_exc()

    systems_and_measurements_json = get_readings_for_tsplot(selected_systemID_list, msr_id_list)
    if 'error' in systems_and_measurements_json:
        raise AttributeError("Error processing API call for measurement readings.")


    return render_template("analyze.html", **locals())


######################################################################
# API call to get metadata of all the systems
######################################################################

# get_all_systems_info() - It returns the system information as a JSON
#                          object.
@dav.route('/aqxapi/get/systems/metadata')
def get_all_systems_info():
    dav_api = DavAPI(get_conn())
    return dav_api.get_all_systems_info()


######################################################################
# API call to get filtering criteria
######################################################################

# get_all_aqx_metadata - It returns all the metadata that are needed
#                        to filter the displayed systems.
@dav.route('/aqxapi/get/systems/filters')
def get_all_aqx_metadata():
    dav_api = DavAPI(get_conn())
    return dav_api.get_all_filters_metadata()


######################################################################
# API call to get latest recorded values of all measurements of a
# given system
######################################################################

@dav.route('/aqxapi/get/system/measurements/<system_uid>', methods=['GET'])
def get_system_measurements(system_uid):
    dav_api = DavAPI(get_conn())
    return dav_api.get_system_measurements(system_uid)


######################################################################
# API call to get latest record of a given measurement of a given
# system
######################################################################

@dav.route('/aqxapi/system/<system_uid>/measurement/<measurement_id>', methods=['GET'])
def get_system_light_measurement(system_uid, measurement_id):
    dav_api = DavAPI(get_conn())
    return dav_api.get_system_measurement(system_uid, measurement_id)


######################################################################
# API call to put a record of a given measurement of a given system
######################################################################

@dav.route('/aqxapi/put/system/measurement', methods=['POST'])
def put_system_measurement():
    dav_api = DavAPI(get_conn())
    data = request.get_json()
    return dav_api.put_system_measurement(data)


######################################################################
# API to get the readings of the time series plot
######################################################################

@dav.route('/aqxapi/get/readings/tsplot/systems/<system_uid_list>/measurements/<msr_id_list>', methods=['GET'])
def get_readings_for_tsplot(system_uid_list, msr_id_list):
    dav_api = DavAPI(get_conn())
    return dav_api.get_readings_for_plot(system_uid_list, msr_id_list)


@dav.route('/aqxapi/get/readings/time_series_plot', methods=['POST'])
def get_readings_for_plot():
    dav_api = DavAPI(get_conn())
    measurements = request.json['measurements']
    systems_uid = request.json['systems']
    return dav_api.get_readings_for_plot(systems_uid, measurements)


######################################################################
# API to get all measurements for picking axis in graph
######################################################################

@dav.route('/aqxapi/get/system/measurement_types', methods=['GET'])
def get_all_measurement_names():
    dav_api = DavAPI(get_conn())
    return dav_api.get_all_measurement_names()


######################################################################
# API to get all measurements' information: id, name, units, min and
# max
######################################################################

@dav.route('/aqxapi/get/system/measurement_info', methods=['GET'])
def get_all_measurement_info():
    dav_api = DavAPI(get_conn())
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
