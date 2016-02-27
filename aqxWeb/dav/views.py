from flask import Blueprint, render_template,request,url_for
from mysql.connector.pooling import MySQLConnectionPool
import os
import json
from app.davAPI import DavAPI

dav = Blueprint('dav', __name__, template_folder='templates')

@dav.route('/home')
def home():
    return "Hi DAV"


# @dav.route('/static')
# def static():
#    return dav.send_static_file('explorePage.html')
    # return dav.send_static_file('static/js/markerclusterer-min.js');

# Set environment variable here to read configuration from environment variable,
# if it does not work add complete path
#os.environ['AQUAPONICS_SETTINGS'] = "system_db.cfg"
#dav.config.from_envvar('AQUAPONICS_SETTINGS')

# To hold db connection pool
pool = None

# Creating object for dav api
davAPI = DavAPI()


# Connect to the database


def init_app():
    create_conn()


######################################################################
# method to get db connection from pool
######################################################################

def get_conn():
    return pool.get_connection()


######################################################################
# method to create connection when application starts
######################################################################

def create_conn():
    global pool
    print("PID %d: initializing pool..." % os.getpid())
    dbconfig = {
         # "host":     dav.config['HOST'],
         # "user":     dav.config['USER'],
         # "passwd":   dav.config['PASS'],
         # "db":       dav.config['DB']

          "host":    '24.18.191.175',
         "user":     'projectfeed',
         "passwd":   'zpL&!k938gUcPuP',
         "db":       'ProjectFeedBoston'

         # "host":    'localhost',
         # "user":     'aquaponics',
         # "passwd":   'aquaponics',
         # "db":       'aquaponics'


         }
    # pool = MySQLConnectionPool(pool_name="mypool", pool_size = dav.config['POOLSIZE'], **dbconfig)

    pool = MySQLConnectionPool(pool_name="mypool", pool_size = 8, **dbconfig)

######################################################################
# UI API
######################################################################

# @dav.route('/')
# @dav.route('/index')
# def index():
#     user = {'nickname': 'Test'}  # fake user
#     return render_template("index.html",
#                            title='Home',
#                            user=user)


# DATA ANALYTICS AND VISUALIZATION APIs

######################################################################
# Interactive map of all active systems
######################################################################

@dav.route('/explore')
def display_explore_page():
    systems_and_info_json = get_all_systems_info()
    systems = json.loads(systems_and_info_json)['systems']
    metadata_json = get_all_aqx_metadata()
    return render_template("explorePage.html", **locals())


######################################################################
# API call to get metadata of a given system
######################################################################

# get_metadata(system_uid) - It takes in the system_uid as the input
#                            parameter and returns the metadata for the
#                            given system. Currently, it returns only
#                            the name of the system.
@dav.route('/aqxapi/get/system/meta/<system_uid>', methods=['GET'])
def get_metadata(system_uid):
    return davAPI.get_system_metadata(get_conn(), system_uid)


######################################################################
# API call to get metadata of all the systems
######################################################################

# get_all_systems_info() - It returns the system information as a JSON
#                          object.
@dav.route('/aqxapi/get/systems/metadata')
def get_all_systems_info():
    return davAPI.get_all_systems_info(get_conn())


######################################################################
# API call to get filtering criteria
######################################################################

# get_all_aqx_metadata - It returns all the metadata that are needed
#                        to filter the displayed systems.
@dav.route('/aqxapi/get/systems/filters')
def get_all_aqx_metadata():
    return davAPI.get_all_filters_metadata(get_conn())


######################################################################
# API call to get user data
######################################################################

@dav.route('/aqxapi/get/user/<uid>', methods=['GET'])
def get_user(uid):
    return davAPI.get_user(get_conn(), uid)


######################################################################
# API call to put user data
######################################################################

@dav.route('/aqxapi/put/user', methods=['POST'])
def put_user():
    user = request.get_json()
    return davAPI.put_user(get_conn(),user)

