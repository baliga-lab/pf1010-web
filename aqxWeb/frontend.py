from flask import Blueprint, render_template, request, session
from mysql.connector.pooling import MySQLConnectionPool
import os
import json
from aqxWeb.app.uiAPI import uiAPI

frontend = Blueprint('frontend', __name__, template_folder='templates',static_folder='static')

pool = None

uiAPI = uiAPI()

# Connect to the database
def init_app(app):
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


@frontend.route('/')
#######################################################################################
# function : index
# purpose : renders home page when user is not logged in
# parameters : None
# returns: index.html page
#######################################################################################
def index():
    return render_template('index.html')


@frontend.route('/about')
#######################################################################################
# function : about
# purpose : renders about page with same information from current aquaponics page
# parameters : None
# returns: about.html page
#######################################################################################
def about():
    return render_template('about.html')


@frontend.route('/system')
#######################################################################################
# function : system
# purpose : renders single system overview page (not yet integrating DAV components)
# parameters : None
# returns: system.html page currently
#######################################################################################
def system():
    return render_template('system.html')


@frontend.route('/add_system')
#######################################################################################
# function : add system
# purpose : renders form to add system
# parameters : None
# returns: add_system.html page
#######################################################################################
def add_system():
    return render_template('add_system.html')


@frontend.route('/settings')
#######################################################################################
# function : settings
# purpose : renders settings page
# parameters : None
# returns: settings.html
#######################################################################################
def settings():
    return render_template('settings.html')


@frontend.route('/coming')
#######################################################################################
# function : coming soon
# purpose : placeholder for pages not yet designed -- will remove later
# parameters : None
# returns: coming.html
#######################################################################################
def coming():
    return render_template('coming.html')

####
#
# SYSTEMS METADATA
#
# ####

@frontend.route('/aqxapi/get/system/meta/<system_uid>', methods=['GET'])
def get_metadata(system_uid):
    return uiAPI.get_system_metadata(get_conn(), system_uid)


######################################################################
# API call to get metadata of all the systems
######################################################################

# get_all_systems_info() - It returns the system information as a JSON
#                          object.
@frontend.route('/aqxapi/get/systems/metadata')
def get_all_systems_info():
    return davAPI.get_all_systems_info(get_conn())


######################################################################
# API call to get filtering criteria
######################################################################

# get_all_aqx_metadata - It returns all the metadata that are needed
#                        to filter the displayed systems.
@frontend.route('/aqxapi/get/systems/filters')
def get_all_aqx_metadata():
    return davAPI.get_all_filters_metadata(get_conn())


######################################################################
# API call to get user data
######################################################################

@frontend.route('/aqxapi/get/user/<uid>', methods=['GET'])
def get_user(uid):
    return davAPI.get_user(get_conn(), uid)


######################################################################
# API call to put user data
######################################################################

@frontend.route('/aqxapi/put/user', methods=['POST'])
def put_user():
    user = request.get_json()
    return davAPI.put_user(get_conn(), user)