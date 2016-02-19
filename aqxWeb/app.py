from dav.app.davAPI import DavAPI
from flask import Flask, render_template, request
import os
import urllib, json
from mysql.connector.pooling import MySQLConnectionPool

#set env variable here to read config from env variable, if it does not work add complete path
os.environ['AQUAPONICS_SETTINGS']="system_db.cfg"

app = Flask(__name__)
app.config.from_envvar('AQUAPONICS_SETTINGS')

#to hold db connection pool
pool = None

#creating object for dav api
davAPI = DavAPI()


#connect to the database


def init_app(app):
    create_conn()

######################################################################
##  method to get db connection from pool
######################################################################
def get_conn():
    return pool.get_connection()

######################################################################
##  method to create connection when application starts
# #####################################################################
def create_conn():
    global pool
    print("PID %d: initializing pool..." % os.getpid())
    dbconfig = {
         "host":     app.config['HOST'],
         "user":     app.config['USER'],
         "passwd":   app.config['PASS'],
         "db":       app.config['DB']
         }
    pool = MySQLConnectionPool(pool_name = "mypool", pool_size = app.config['POOLSIZE'], **dbconfig)

######################################################################
##  UI API
######################################################################
@app.route('/')
@app.route('/index')
def index():
    user = {'nickname': 'Test'}  # fake user
    return render_template("index.html",
                           title='Home',
                           user=user)


######################################################################
##  Interactive map of all active systems
######################################################################
@app.route('/explore')
def display_explore_page():
    systems_and_info_json = get_all_systems_info()
    metadata_json = get_all_aqx_metadata()
    return render_template("dav/explorePage.html", **locals())


######################################################################
##  Test page for pin filtering
######################################################################
@app.route('/filtertest')
def filterTest():
    return render_template("dav/DAVindex.html")

######################################################################
##  Test page for weather widget
######################################################################
@app.route('/weathertest')
def weather():
    return render_template("dav/weatherTest.html")

######################################################################
##  Data Analytics and Viz. API
######################################################################


######################################################################
##  API call to get systems data
######################################################################
@app.route('/aqxapi/get/systems')
def get_systems():
    davAPI = DavAPI()
    return davAPI.get_all_systems(get_conn())

######################################################################
##  API call to get metadata of a given system
######################################################################

@app.route('/aqxapi/get/system/meta/<system_uid>', methods=['GET'])
def get_metadata(system_uid):
    return davAPI.get_system_metadata(get_conn(), system_uid)


######################################################################
##  API call to get metadata of all the systems
######################################################################

@app.route('/aqxapi/get/systems/metadata')
def get_all_systems_info():
    return davAPI.get_all_systems_info(get_conn())

######################################################################
##  API call to get filtering criteria
######################################################################

@app.route('/aqxapi/get/systems/filters')
def get_all_aqx_metadata():
    return davAPI.get_all_filters_metadata(get_conn())

######################################################################
##  API call to get user data
######################################################################

@app.route('/aqxapi/get/user/<uid>' ,methods=['GET'])
def get_user(uid):
    return davAPI.get_user(get_conn(),uid)

######################################################################
##  API call to put user data
######################################################################

@app.route('/aqxapi/put/user' ,methods=['POST'])
def put_user():
    user = request.get_json()
    return davAPI.put_user(get_conn(),user)

######################################################################
##  Social Components API
######################################################################




#common init method for application
if __name__ == "__main__":
    init_app(app)
    app.run(debug=True)
