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

# Creating object for dav api
davAPI = DavAPI()

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



######################################################################
# Interactive map of all active systems
######################################################################
# @dav.route('/conf')
# def print_conf():
#     Config = ConfigParser.ConfigParser()
#     Config.read("./dav/system_db.ini")
#     print Config.sections()
#     print ConfigSectionMap("Aqx")['pass']
#     print ConfigSectionMap("Aqx")['poolsize']
#
#     return "conf printed"

@dav.route('/')
#######################################################################################
# function : index
# purpose : placeholder for dav.index
# parameters : None
# returns: Index string... no purpose
#######################################################################################
def index():
    return 'Index'


@dav.route('/explore')
def explore():
    systems_and_info_json = get_all_systems_info()
    systems = json.loads(systems_and_info_json)['systems']
    metadata_json = get_all_aqx_metadata()
    return render_template("explore.html", **locals())


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

if __name__ == '__main__':
    init_app()