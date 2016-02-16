from dav.app.davAPI import DavAPI
from flask import Flask, render_template
import os
from mysql.connector.pooling import MySQLConnectionPool
#set env variable here to read config from env variable
# os.environ['AQUAPONICS_SETTINGS']="C:\\Users\\Brian\\Documents\\GitHub\\aqxWeb-NEU\\aqxWeb\system_db.cfg"
app = Flask(__name__)
app.config.from_envvar('AQUAPONICS_SETTINGS')
#to hold db connection pool
pool = None

def init_app(app):
    # connect to the database
    create_conn()

######################################################################
##  method to get db connection from pool
######################################################################
def get_conn():
    return pool.get_connection()

######################################################################
##  method to create connection when application starts
######################################################################
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
    json_obj = filter(lambda x: (x['lat'] and x['lng']), json_obj)

    return render_template("dav/mapPage.html", json_obj=json_obj)


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

@app.route('/aqxapi/getsystem/meta/<system_uid>', methods=['GET'])
def get_metadata(system_uid):
    print system_uid
    davAPI = DavAPI()
    return davAPI.get_system_metadata(get_conn(), system_uid)


######################################################################
##  API call to get metadata of all the systems
######################################################################

@app.route('/aqxapi/get/systems/metadata')
def get_all_systems_info():
    davAPI = DavAPI()
    return davAPI.get_all_systems_info(get_conn())



######################################################################
##  Social Components API
######################################################################
#init method for application
if __name__ == "__main__":
    init_app(app)
    app.run(debug=True)