from flask import Blueprint, render_template, request, session

from app.uiAPI import UiAPI
from app.APIv2 import API

import json

frontend = Blueprint('frontend', __name__, template_folder='templates', static_folder='static')

pool = None


# Connect to the database
def init_app(gpool, gapp):
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


@frontend.route('/contact', methods=['GET'])
def contact():
    return render_template('contact.html')


@frontend.route('/system')
def system():
    return render_template('system.html')


@frontend.route('/create_system_page')
def create_system_page():
    enums = json.loads(getEnums())
    return render_template('create_system.html', **locals())


@frontend.route('/badges')
def badges():
    return render_template('badges.html')


#########################
#                       #
#  METADATA ROUTES      #
#                       #
#########################
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


#########################
#                       #
#  USER ROUTES          #
#                       #
#########################
######################################################################
# API call to get user data
######################################################################
# @frontend.route('/aqxapi/get/user/<uid>', methods=['GET']) google sheet removed get user by user id. i leave it here just in case.
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


#########################
#                       #
#  SYSTEM ROUTES        #
#                       #
#########################
######################################################################
# API call to get all systems
# get_all_systems) - It returns List of all aquaponics systems,
# system_uid,name,user_id owning the system longitude and latitude
# of system's location as a JSON object.
######################################################################
@frontend.route('/aqxapi/v1/systems', methods=['GET'])
def get_systems():
    uiAPI = UiAPI(get_conn())
    return uiAPI.get_systems()


######################################################################
# API call to check if the system exists
# check_system_exists) - It returns "If system exists:
# {"status":"True"}
# If system does not exist:
# {"status":"False"}
######################################################################
@frontend.route('/aqxapi/v1/system/exists/<system_uid>', methods=['GET'])
def check_system_exists(system_uid):
    uiAPI = UiAPI(get_conn())
    return uiAPI.check_system_exists(system_uid)


######################################################################
# API call to get all user systems
######################################################################
@frontend.route('/aqxapi/v1/user/<user_id>/systems', methods=['GET'])
def get_all_user_systems(user_id):
    uiAPI = UiAPI(get_conn())
    return uiAPI.get_all_user_systems(user_id)


#########################
#                       #
#  IMAGE ROUTES         #
#                       #
#########################
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


#########################
#                       #
#  ANNOTATION ROUTES    #
#                       #
#########################
# add an annotation to system annotation table
@frontend.route('/aqxapi/v1/system/<system_id>/annotations', methods=['POST'])
def add_annotation(system_id):
    uiAPI = UiAPI(get_conn())
    # annotation_name = request.form['mySelect']
    annotation_num = request.form['number']
    return uiAPI.add_annotation(system_id, annotation_num)


# view a system's all annotations
@frontend.route('/aqxapi/v1/system/<system_id>/annotations', methods=['GET'])
def view_annotation(system_id):
    try:
        uiAPI = UiAPI(get_conn())
        return uiAPI.view_annotation(system_id)
    except Exception as ex:
        print "Exception : " + str(ex.message)


# get status by given system uID
@frontend.route('/aqxapi/v1/system/<system_uid>/status', methods=['GET'])
def get_status_by_system_uid(system_uid):
    uiAPI = UiAPI(get_conn())
    return uiAPI.get_status_by_system_uid(system_uid)


# get system id by given system uID
# test purpose
@frontend.route('/aqxapi/v1/system/<user_id>/<name>', methods=['GET'])
def get_system_id_and_system_uid_with_user_id_and_system_name(user_id, name):
    uiAPI = UiAPI(get_conn())
    return uiAPI.get_system_id_and_system_uid_with_user_id_and_system_name(user_id, name)


######################################################################
# API Overhaul
######################################################################

@frontend.route('/aqxapi/v2/user/<googleID>', methods=['GET'])
def getUserID(googleID):
    api = API(get_conn())
    return api.getUserID(googleID)


@frontend.route('/aqxapi/v2/user/<userID>/system', methods=['GET'])
def getSystemsForUser(userID):
    api = API(get_conn())
    return api.getSystemsForUser(userID)


@frontend.route('/aqxapi/v2/system/<systemUID>', methods=['GET'])
def getSystem(systemUID):
    api = API(get_conn())
    return api.getSystem(systemUID)


@frontend.route('/aqxapi/v2/system', methods=['POST'])
def createSystem():
    api = API(get_conn())
    system = request.get_json()
    system['userID'] = session['uid']
    return api.createSystem(system)


@frontend.route('/aqxapi/v2/system/<systemUID>', methods=['DELETE'])
def deleteSystem(systemUID):
    api = API(get_conn())
    return api.deleteSystem(systemUID)


@frontend.route('/aqxapi/v2/enums', methods=['GET'])
def getEnums():
    api = API(get_conn())
    return api.getEnums()


@frontend.route('/aqxapi/v1/mailing', methods = ['POST'])
def subscribe():
    api = API(get_conn())
    email = request.get_json()['email']
    print(email)
    return api.subscribe(email)


@frontend.route('/aqxapi/v2/annotation/<annotationID>', methods=['GET'])
def getReadableAnnotation(annotationID):
    api = API(get_conn())
    return api.getReadableAnnotation(annotationID)
