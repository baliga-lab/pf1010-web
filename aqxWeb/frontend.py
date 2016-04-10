from flask import Blueprint, render_template, request, session
from mysql.connector.pooling import MySQLConnectionPool
import os
from app.uiAPI import UiAPI
from sc.app.scAPI import ScAPI

frontend = Blueprint('frontend', __name__, template_folder='templates',static_folder='static')

pool = None

# Connect to the database
def init_app(gpool,gapp):
    global pool
    pool = gpool
    global app
    app = gapp

def get_app():
    return app

######################################################################
# method to get db connection from pool
######################################################################

def get_conn():
    return pool.get_connection()


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

#########################
#                       #
#  SYSTEMS METADATA     #
#                       #
# #######################


######################################################################
# API call to get metadata of a given system
######################################################################
@frontend.route('/aqxapi/v1/system/meta/<system_uid>', methods=['GET'])
def get_metadata(system_uid):
    uiAPI = UiAPI(get_conn())
    return uiAPI.get_system_with_system_id(system_uid)

######################################################################
# API call to delete metadata of a given system
######################################################################

@frontend.route('/aqxapi/v1/system/meta/<system_uid>', methods=['DELETE'])
def delete_metadata(system_uid):
    uiAPI = UiAPI(get_conn())
    return uiAPI.delete_metadata(system_uid)


######################################################################
# API call to get metadata of all the systems
######################################################################

# get_all_systems_info() - It returns the system information as a JSON
#                          object.
@frontend.route('/aqxapi/get/systems/metadata')
def get_all_systems_info():
    uiAPI = UiAPI(get_conn())
    return uiAPI.get_all_systems_info()


######################################################################
# API call to get filtering criteria
######################################################################

# get_all_aqx_metadata - It returns all the metadata that are needed
#                        to filter the displayed systems.
@frontend.route('/aqxapi/get/systems/filters')
def get_all_aqx_metadata():
    uiAPI = UiAPI(get_conn())
    return uiAPI.get_all_filters_metadata()


######################################################################
# API call to get user data
######################################################################

#@frontend.route('/aqxapi/get/user/<uid>', methods=['GET']) google sheet removed get user by user id. i leave it here just in case.
def get_user(uid):
    uiAPI = UiAPI(get_conn())
    return uiAPI.get_user(uid)


######################################################################
# API call to get user data with googleid
######################################################################

@frontend.route('/aqxapi/get/user/<googleid>', methods=['GET'])
def get_user_with_google_id(googleid):
    uiAPI = UiAPI(get_conn())
    return uiAPI.get_user_with_google_id(googleid)


######################################################################
# API call to put user data
######################################################################

@frontend.route('/aqxapi/put/user', methods=['POST'])
def put_user():
    user = request.get_json()
    uiAPI = UiAPI(get_conn())
    return uiAPI.put_user(user)


######################################################################
# API call to inserting user data
######################################################################

@frontend.route('/aqxapi/post/user', methods=['POST'])
def insert_user():
    user = request.get_json()
    uiAPI = UiAPI(get_conn())
    return uiAPI.insert_user(user)


######################################################################
# API call to get all systems
# get_all_systems) - It returns List of all aquaponics systems,
# system_uid,name,user_id owning the system longitude and latitude
# of system's location as a JSON object.
######################################################################
@frontend.route('/aqxapi/get/systems')
def get_systems():
    uiAPI = UiAPI(get_conn())
    return uiAPI.get_systems()


######################################################################
# API call to Check if the system exists
# check_system_exists) - It returns "If system exists:
#{"status":"True"}
#If system does not exist:
#{"status":"False"}
######################################################################

@frontend.route('/aqxapi/system/exists/<system_uid>',methods=['GET'])
def check_system_exists(system_uid):
    uiAPI = UiAPI(get_conn())
    return uiAPI.check_system_exists(system_uid)

######################################################################
# API call to create system both in ui and sc database  
######################################################################

@frontend.route('/create_system', methods=['POST'])
def create_system():
    system = request.form
    #name, date_created, aqx_technique, gb_media, crop, num_crop, organism, num_org, lat, long

    # system_name = request.form['name'] # this is wrong
    # system_start_date = request.form['date_created']
    # system_aqx_technique_id = request.form['aqx_technique']
    # system_gb_media = request.form['gb_media']
    # system_crop = request.form['crop']
    # system_num_crop = request.form['num_crop']
    # system_organism = request.form['organism']
    # system_num_org = request.form['num_org']
    # system_location_lat = request.form['lat']
    # system_location_lng = request.form['long']

    #  system_user_id = session['uid']



    #jsonForNeo4jObject=
    # system_json = {
    #     "system_id": system_id,    #get this from mysql db after system is inserted into mysql db.
    #     "system_uid": system_uid,
    #     "name": "Test SC API System",
    #     "description": "Test SC API System Description", //make it the same as 'name'
    #     "location_lat": 42.33866,
    #     "location_lng": -71.092186,
    #     "status": 0
    # }
    # systemJSONObject = json.dumps({'user': sql_id, 'system': system_json})
    # call sc api to create system and insert system into their DB
    # with get_app().test_client() as client:
    #     response = client.post('/social/aqxapi/v1/system', data=system, content_type='application/json')

    uiAPI = UiAPI(get_conn())
    return uiAPI.create_system(system)

######################################################################
# API call to get all user systems
######################################################################

@frontend.route('/aqxapi/get/user/<user_id>/systems', methods=['GET'])
def get_all_user_systems(user_id):
    uiAPI = UiAPI(get_conn())
    return uiAPI.get_all_user_systems(user_id)

######################################################################
# API call to add an image to a system_image table
######################################################################
@frontend.route('/aqxapi/post/system/<system_uid>/image', methods=['POST'])
def add_image_to_system(system_uid):
    image = request.form
    uiAPI = UiAPI(get_conn())
    return uiAPI.add_image_to_system(system_uid, image)

######################################################################
# API call to delete an image from a system
######################################################################
@frontend.route('/aqxapi/delete/system/<system_uid>/image/<image_id>', methods=['DELETE'])
def delete_image_from_system(system_uid, image_id):
    uiAPI = UiAPI(get_conn())
    return uiAPI.delete_image_from_system(system_uid, image_id)

######################################################################
# API call to view an image of a system
######################################################################
@frontend.route('/aqxapi/get/system/<system_uid>/image/<image_id>', methods=['GET'])
def view_image_from_system(system_uid, image_id):
    uiAPI = UiAPI(get_conn())
    return uiAPI.view_image_from_system(system_uid, image_id)

######################################################################
# API call to view a system's all images
######################################################################
@frontend.route('/aqxapi/get/system/<system_uid>/images', methods=['GET'])

def get_system_all_images(system_uid):
    uiAPI = UiAPI(get_conn())
    return uiAPI.get_system_all_images(system_uid)

# add an annotation to system annotation table
@frontend.route('/aqxapi/post/system/<system_uid>/annotations', methods=['POST'])

def add_annotation(system_uid):
    uiAPI = UiAPI(get_conn())
    annotation = request.form
    return uiAPI.add_annotation(system_uid, annotation)
#view a system's all annotations
@frontend.route('/aqxapi/get/system/<system_uid>/annotations', methods=['GET'])
def view_annotation(system_uid):
    uiAPI = UiAPI(get_conn())
    return uiAPI.view_annotation(system_uid)





