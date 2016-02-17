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
@app.route('/map')
def displayMapPage():
    # json_obj = bostonapi.get_systems_and_metadata()
    # url = "http://localhost:5000/aqxapi/get/systems"
    # response = urllib.urlopen(url)
    MOCK = False
    if (MOCK):
        json_obj = [{"title": "System1", "lat": 59.3, "lng": 18.1, "description": {"aqx_techniques":"Nutrient Film Technique (NFT)",
                                                                                   "aqx_organism":"Blue Tilapia",
                                                                                   "growbed_media":"Clay Pebbles",
                                                                                   "crop":"Lettuce"}},
                    {"title": "System2", "lat": 59.9, "lng": 10.8, "description": {"aqx_techniques":"Ebb and Flow (Media-based)",
                                                                                   "aqx_organism":"Mozambique Tilapia",
                                                                                   "growbed_media":"Coconut Coir",
                                                                                   "crop":"Bok Choy"}},
                    {"title": "System3", "lat": 55.7, "lng": 12.6, "description": {"aqx_techniques": "Floating Raft",
                                                                                   "aqx_organism":"Koi",
                                                                                   "growbed_media":"Seed Starter Plugs",
                                                                                   "crop":"Carrot"}}]
        #Having trouble with filtering on the fly, using this for now
        json_obj = filter(lambda x: (x['lat'] and x['lng']), json_obj)
    else:
        json_obj = get_all_systems_info()

    print str(json_obj)
    metadata_json = {"aqx_techniques":["Nutrient Film Technique (NFT)", "Ebb and Flow (Media-based)", "Floating Raft", "Vertical Flow Through"],
                     "aqx_organisms":["Mozambique Tilapia", "Bluegill", "Shrimp", "Nile Tilapia", "Blue Tilapia", "Koi", "Goldfish", "Betta Fish"],
                     "growbed_media":["Clay Pebbles", "Coconut Coir", "Seed Starter Plugs"],
                     "crops": ["Bok Choy", "Carrot", "Lettuce", "Pea", "Strawberry"]}

    return render_template("dav/mapPage.html", json_obj=json_obj, metadata_json=metadata_json)

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
