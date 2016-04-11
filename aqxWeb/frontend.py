from flask import Blueprint, render_template, request, session
from mysql.connector.pooling import MySQLConnectionPool
import os
from app.uiAPI import UiAPI
from sc.app.scAPI import ScAPI
import uuid
import json
import datetime
from datetime import datetime

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
def index():
    return render_template('index.html')


@frontend.route('/about')
def about():
    return render_template('about.html')


@frontend.route('/resources')
def resources():
    return render_template('resources.html')


@frontend.route('/curriculum')
def curriculum():
    return render_template('curriculum.html')


@frontend.route('/system')
def system():
    return render_template('system.html')


@frontend.route('/create_system')
def add_system():
    return render_template('create_system.html')


@frontend.route('/badges')
def badges():
    return render_template('badges.html')

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
@frontend.route('/aqxapi/v1/systems/metadata', methods=['GET'])
def get_all_systems_info():
    uiAPI = UiAPI(get_conn())
    return uiAPI.get_all_systems_info()


######################################################################
# API call to get filtering criteria
######################################################################

# get_all_aqx_metadata - It returns all the metadata that are needed
#                        to filter the displayed systems.
@frontend.route('/aqxapi/v1/systems/filters', methods=['GET'])
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

@frontend.route('/aqxapi/v1/user/<googleid>', methods=['GET'])
def get_user_with_google_id(googleid):
    uiAPI = UiAPI(get_conn())
    return uiAPI.get_user_with_google_id(googleid)


######################################################################
# API call to put user data
######################################################################

@frontend.route('/aqxapi/v1/user', methods=['POST'])
def put_user():
    user = request.get_json()
    uiAPI = UiAPI(get_conn())
    return uiAPI.put_user(user)


######################################################################
# API call to inserting user data
######################################################################

@frontend.route('/aqxapi/v1/user', methods=['POST'])
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
@frontend.route('/aqxapi/v1/systems',methods=['GET'])
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

@frontend.route('/aqxapi/v1/system/exists/<system_uid>',methods=['GET'])
def check_system_exists(system_uid):
    uiAPI = UiAPI(get_conn())
    return uiAPI.check_system_exists(system_uid)

######################################################################
# API call to create system both in ui and sc database
######################################################################

@frontend.route('/aqxapi/v1/system/create', methods=['POST'])
def create_system():
    try:
        uiAPI = UiAPI(get_conn())
        # ui create system accepts a system json object
        #system_json_ui = request.get_json() #verena's json format may be wrong


        #get field value one by one and  put em into a json for crop, org, gb tables and sc api call to create system
        # in sc database

        system_user_id = session['uid']
        system_name = request.form['system_name']
        system_start_date = request.form['start_date']
        system_aqx_technique_id = request.form['aqx_technique_id']
        system_location_lat = request.form['lat']
        system_location_lng = request.form['long']

        # create system json for ui's create system
        system_json_ui = {
            'user_id': system_user_id,
            'name': system_name,
            'start_date': system_start_date,
            'aqx_technique_id': system_aqx_technique_id,
            'creation_time': str(datetime.now().time()),
            'location_lat': system_location_lat,
            'location_lng': system_location_lng
        }
        uiAPI.create_system(system_json_ui)

        #get the newly created system's system id , not system_uid
        #system id will be used by crop, org, gb_media and sc api all to created system
        system_id_and_uid_json = uiAPI.get_system_id_and_system_uid_with_user_id_and_system_name(system_user_id,system_json_ui.get('name'))
        system_id_and_uid_data = json.loads(system_id_and_uid_json)
        system_id = system_id_and_uid_data['system']['system_id']
        system_uid = system_id_and_uid_data['system']['system_uid']


        #system gb media table
        system_gb_media = request.form['gb_media']
        system_num_gb = request.form['num_gb']
        system_gb_media_json = {
            "system_id": system_id,
            "gb_media_id": system_gb_media,
            "num": system_num_gb
        }
        uiAPI.create_system_gb_media_table(system_gb_media_json)


        #system crops table
        system_crop = request.form['crop']
        system_num_crop = request.form['num_crop']
        system_crop_json = {
            "system_id": system_id,
            "crop_id": system_crop,
            "num": system_num_crop
        }
        uiAPI.create_system_crop_table(system_crop_json)

        # system_aquatic_organisms table
        system_organism = request.form['organism']
        system_num_org = request.form['num_org']
        system_aquatic_organisms_json = {
            "system_id": system_id,
            "organism_id": system_organism,
            "num": system_num_org
        }
        uiAPI.create_system_quatic_organisms_table(system_aquatic_organisms_json)




        # calling sc api to create system into sc database
        #jsonForNeo4jObject
        system_json = {
            "system_id": system_id,    #get this from mysql db after system is inserted into mysql db.
            "system_uid": system_uid, #needs to be a string
            "name": system_name,
            "description": system_name, #make it the same as 'name'
            "location_lat": system_location_lat,
            "location_lng": system_location_lng,
            "status": 100
        }
        systemJSONObject = json.dumps({'user': system_user_id, 'system': system_json})


        # #mocked data test for success
        # system_json = {
        #     "system_id": 111111,
        #     "system_uid": "2wdf2tytpw",
        #     "name": "Zhibo System",
        #     "description": "UI Zhibo API System Description",
        #     "location_lat": 42.33866,
        #     "location_lng": -71.092186,
        #     "status": 0
        # }
        print system_json
        #systemJSONObject = json.dumps({'user': 57, 'system': system_json})
        with get_app().test_client() as client:
            response = client.post('/social/aqxapi/v1/system', data=systemJSONObject, content_type='application/json')
            #print response
            result = json.loads(response.data)
            #print result
        return render_template("system.html")
    except Exception as ex:
        print "Exception : "+ str(ex.message)


    #return uiAPI.create_system(system)

######################################################################
# API call to get all user systems
######################################################################

@frontend.route('/aqxapi/v1/user/<user_id>/systems', methods=['GET'])
def get_all_user_systems(user_id):
    uiAPI = UiAPI(get_conn())
    return uiAPI.get_all_user_systems(user_id)

######################################################################
# API call to add an image to a system_image table
######################################################################
@frontend.route('/aqxapi/v1/system/<system_uid>/image', methods=['POST'])
def add_image_to_system(system_uid):
    image = request.form
    uiAPI = UiAPI(get_conn())
    return uiAPI.add_image_to_system(system_uid, image)

######################################################################
# API call to delete an image from a system
######################################################################
@frontend.route('/aqxapi/v1/system/<system_uid>/image/<image_id>', methods=['DELETE'])
def delete_image_from_system(system_uid, image_id):
    uiAPI = UiAPI(get_conn())
    return uiAPI.delete_image_from_system(system_uid, image_id)

######################################################################
# API call to view an image of a system
######################################################################
@frontend.route('/aqxapi/v1/system/<system_uid>/image/<image_id>', methods=['GET'])
def view_image_from_system(system_uid, image_id):
    uiAPI = UiAPI(get_conn())
    return uiAPI.view_image_from_system(system_uid, image_id)

######################################################################
# API call to view a system's all images
######################################################################
@frontend.route('/aqxapi/v1/system/<system_uid>/images', methods=['GET'])

def get_system_all_images(system_uid):
    uiAPI = UiAPI(get_conn())
    return uiAPI.get_system_all_images(system_uid)

# add an annotation to system annotation table
@frontend.route('/aqxapi/v1/system/<system_uid>/annotations', methods=['POST'])

def add_annotation(system_uid):
    uiAPI = UiAPI(get_conn())
    annotation = request.form
    return uiAPI.add_annotation(system_uid, annotation)
#view a system's all annotations
@frontend.route('/aqxapi/v1/system/<system_uid>/annotations', methods=['GET'])
def view_annotation(system_uid):
    uiAPI = UiAPI(get_conn())
    return uiAPI.view_annotation(system_uid)

#get status by given system uID
@frontend.route('/aqxapi/v1/system/<system_uid>/status', methods=['GET'])
def get_status_by_system_uid(system_uid):
    uiAPI = UiAPI(get_conn())
    return uiAPI.get_status_by_system_uid(system_uid)


#get system id by given system uID
#test purpose
@frontend.route('/aqxapi/v1/system/<user_id>/<name>', methods=['GET'])
def get_system_id_and_system_uid_with_user_id_and_system_name(user_id,name):
    uiAPI = UiAPI(get_conn())
    return uiAPI.get_system_id_and_system_uid_with_user_id_and_system_name(user_id,name)

# work with mocked data
# @frontend.route('/aqxapi/v1/system/gb_media', methods=['POST'])
# def create_system_gb_media_table():
#     uiAPI = UiAPI(get_conn())
#     return uiAPI.create_system_gb_media_table()

# worked wiht mocked data
# @frontend.route('/aqxapi/v1/system/crop', methods=['POST'])
# def create_system_crop_table():
#     uiAPI = UiAPI(get_conn())
#     return uiAPI.create_system_crop_table()
#

#worked with mocked data
# @frontend.route('/aqxapi/v1/system/org', methods=['POST'])
# def create_system_quatic_organisms_table():
#     uiAPI = UiAPI(get_conn())
#     return uiAPI.create_system_quatic_organisms_table()







