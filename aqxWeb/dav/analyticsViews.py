
from flask import Blueprint, render_template,request,url_for
from mysql.connector.pooling import MySQLConnectionPool
import os
import json
from app.davAPI import DavAPI

dav = Blueprint('dav', __name__, template_folder='templates',static_folder='static')


@dav.route('/home')
def home():
    return "Data Analytics and Viz Homepage"

# To hold db connection pool
pool = None

# Connect to the database
def init_app(app):
    app.debug = True
    app.config.from_envvar('AQUAPONICS_SETTINGS')
    create_conn(app)


######################################################################
# method to get db connection from pool
######################################################################

def get_conn():
    return pool.get_connection()


######################################################################
# method to create connection when application starts
######################################################################

def create_conn(app):

    global pool
    print("PID %d: initializing pool..." % os.getpid())
    dbconfig = {
        "host":     app.config['HOST'],
        "user":     app.config['USER'],
        "passwd":   app.config['PASS'],
        "db":       app.config['DB']
    }

    pool = MySQLConnectionPool(pool_name="mypool", pool_size = app.config['POOLSIZE'], **dbconfig)


######################################################################
# Interactive map of all active systems
######################################################################
@dav.route('/explore')
def explore():
    systems_and_info_json = get_all_systems_info()
    systems = json.loads(systems_and_info_json)['systems']
    metadata_json = get_all_aqx_metadata()
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
def analyzeGraph():
    systems_and_measurements_json = \
        {'response':
            [
                { 'name': 'system_12345' ,
                  'system_uid': '12344',
                  'measurement': [
                      { 'type': 'pH',
                        'values':
                            [{ 'x' : 0, 'y' : 7.0, 'date': '03:03:16:00' },
                             { 'x' : 1, 'y' : 11.0, 'date': '03:03:16:01'},
                             { 'x' : 2, 'y' : 9.2, 'date': '03:03:16:02' }]
                        },
                      { 'type': 'nitrate',
                        'values':
                            [{ 'x' : 8, 'y' : 3.5, 'date': '03:01:16:12'},
                             { 'x' : 16, 'y' : 0.5, 'date': '03:02:00:12'}]
                        }
                  ]
                  },
                { 'name': 'system_23145',
                  'system_uid': '23145',
                  'measurement':
                      [
                          { 'type': 'pH',
                            'values':
                                [{ 'x' : 5, 'y' : 6.0, 'date': '03:03:16:00' },
                                 { 'x' : 6, 'y' : 9.0, 'date': '03:03:16:01' },
                                 { 'x' : 10, 'y' : 14.0, 'date': '03:03:16:02' }]
                            },
                          { 'type': 'nitrate',
                            'values':
                                [{ 'x' : 1, 'y' : 6.5, 'date': '03:01:16:12'},
                                 { 'x' : 7, 'y' : 6.5, 'date': '03:01:22:12'},
                                 { 'x' : 9, 'y' : 1.5, 'date': '03:02:00:12'}]
                            }
                      ]
                  }
            ]
        }

    systems_and_measurements_json = systems_and_measurements_json['response']
    selected_systemID_list = ["system_12345", "system_54321"]
    measurement_types = ["Nitrate", "Nitrite", "Hardness", "Chlorine", "Alkalinity", "pH", "Ammonia", "Water Temp", "Light intensity",
                         "Light wavelength","Light intensity","DO","NO3","NH4","Day length","Conductivity"]

    # get measurement information
    # text = request.form['text']
    # content = request.json
    # data = json.dumps(request.form.get('selectedSystems'))

    return render_template("analyze.html", **locals())


######################################################################
# API call to get metadata of a given system
######################################################################

# get_metadata(system_uid) - It takes in the system_uid as the input
#                            parameter and returns the metadata for the
#                            given system. Currently, it returns only
#                            the name of the system.
@dav.route('/aqxapi/get/system/meta/<system_uid>', methods=['GET'])
def get_metadata(system_uid):
    davAPI = DavAPI(get_conn())
    return davAPI.get_system_metadata(system_uid)


######################################################################
# API call to get metadata of all the systems
######################################################################

# get_all_systems_info() - It returns the system information as a JSON
#                          object.
@dav.route('/aqxapi/get/systems/metadata')
def get_all_systems_info():
    davAPI = DavAPI(get_conn())
    return davAPI.get_all_systems_info()


######################################################################
# API call to get filtering criteria
######################################################################

# get_all_aqx_metadata - It returns all the metadata that are needed
#                        to filter the displayed systems.
@dav.route('/aqxapi/get/systems/filters')
def get_all_aqx_metadata():
    davAPI = DavAPI(get_conn())
    return davAPI.get_all_filters_metadata()


######################################################################
# API call to get user data
######################################################################

@dav.route('/aqxapi/get/user/<uid>', methods=['GET'])
def get_user(uid):
    davAPI = DavAPI(get_conn())
    return davAPI.get_user(uid)


######################################################################
# API call to put user data
######################################################################

@dav.route('/aqxapi/put/user', methods=['POST'])
def put_user():
    davAPI = DavAPI(get_conn())
    user = request.get_json()
    return davAPI.put_user(user)


######################################################################
# API call to get latest recorded values of all measurements of a
# given system
######################################################################

@dav.route('/aqxapi/get/system/measurements/<system_uid>', methods=['GET'])
def get_system_measurements(system_uid):
    davAPI = DavAPI(get_conn())
    return davAPI.get_system_measurements(system_uid)


######################################################################
# API call to get latest record of a given measurement of a given
# system
######################################################################

@dav.route('/aqxapi/system/<system_uid>/measurement/<measurement_id>', methods=['GET'])
def get_system_light_measurement(system_uid, measurement_id):
    davAPI = DavAPI(get_conn())
    return davAPI.get_system_measurement(system_uid, measurement_id)


######################################################################
# API call to put a record of a given measurement of a given system
######################################################################

@dav.route('/aqxapi/put/system/measurement', methods=['POST'])
def put_system_measurement():
    davAPI = DavAPI(get_conn())
    data = request.get_json()
    return davAPI.put_system_measurement(data)


######################################################################
# API to get the readings of the time series plot
######################################################################

@dav.route('/aqxapi/get/readings/time_series_plot', methods=['POST'])
def get_readings_for_plot():
    davAPI = DavAPI(get_conn())
    data = request.get_json()
    return davAPI.get_readings_for_plot(data)

######################################################################
# API to get all measurements for picking axis in graph
######################################################################

@dav.route('/aqxapi/get/system/measurement_types', methods=['GET'])
def get_all_measurement_names():
    davAPI = DavAPI(get_conn())
    return davAPI.get_all_measurement_names()


if __name__ == '__main__':
    init_app()