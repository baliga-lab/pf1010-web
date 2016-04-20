from flask import request
from frontend import frontend
from app.uiAPI import UiAPI
import MySQLdb

def init_app(flask_app):
    global app
    app = flask_app


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
    uiAPI = UiAPI(app)
    return uiAPI.get_system_with_system_id(system_uid)


######################################################################
# API call to delete metadata of a given system
######################################################################
@frontend.route('/aqxapi/v1/system/meta/<system_uid>', methods=['DELETE'])
def delete_metadata(system_uid):
    uiAPI = UiAPI(app)
    return uiAPI.delete_metadata(system_uid)


######################################################################
# API call to get metadata of all the systems
######################################################################
# get_all_systems_info() - It returns the system information as a JSON
#                          object.
@frontend.route('/aqxapi/v1/systems/metadata', methods=['GET'])
def get_all_systems_info():
    uiAPI = UiAPI(app)
    return uiAPI.get_all_systems_info()


######################################################################
# API call to get filtering criteria
######################################################################
# get_all_aqx_metadata - It returns all the metadata that are needed
#                        to filter the displayed systems.
@frontend.route('/aqxapi/v1/systems/filters', methods=['GET'])
def get_all_aqx_metadata():
    uiAPI = UiAPI(app)
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
    uiAPI = UiAPI(app)
    return uiAPI.get_user(uid)


######################################################################
# API call to get user data with googleid
######################################################################
@frontend.route('/aqxapi/v1/user/<googleid>', methods=['GET'])
def get_user_with_google_id(googleid):
    uiAPI = UiAPI(app)
    return uiAPI.get_user_with_google_id(googleid)


######################################################################
# API call to put user data
######################################################################
@frontend.route('/aqxapi/v1/user', methods=['POST'])
def put_user():
    user = request.get_json()
    uiAPI = UiAPI(app)
    return uiAPI.put_user(user)


######################################################################
# API call to inserting user data
######################################################################
@frontend.route('/aqxapi/v1/user', methods=['POST'])
def insert_user():
    user = request.get_json()
    uiAPI = UiAPI(app)
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
    uiAPI = UiAPI(app)
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
    uiAPI = UiAPI(app)
    return uiAPI.check_system_exists(system_uid)


######################################################################
# API call to get all user systems
######################################################################
@frontend.route('/aqxapi/v1/user/<user_id>/systems', methods=['GET'])
def get_all_user_systems(user_id):
    uiAPI = UiAPI(app)
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
    uiAPI = UiAPI(app)
    return uiAPI.add_image_to_system(system_uid, image)


######################################################################
# API call to delete an image from a system
######################################################################
@frontend.route('/aqxapi/v1/system/<system_uid>/image/<image_id>', methods=['DELETE'])
def delete_image_from_system(system_uid, image_id):
    uiAPI = UiAPI(app)
    return uiAPI.delete_image_from_system(system_uid, image_id)


######################################################################
# API call to view an image of a system
######################################################################
@frontend.route('/aqxapi/v1/system/<system_uid>/image/<image_id>', methods=['GET'])
def view_image_from_system(system_uid, image_id):
    uiAPI = UiAPI(app)
    return uiAPI.view_image_from_system(system_uid, image_id)


######################################################################
# API call to view a system's all images
######################################################################
@frontend.route('/aqxapi/v1/system/<system_uid>/images', methods=['GET'])
def get_system_all_images(system_uid):
    uiAPI = UiAPI(app)
    return uiAPI.get_system_all_images(system_uid)


#########################
#                       #
#  ANNOTATION ROUTES    #
#                       #
#########################
# add an annotation to system annotation table
@frontend.route('/aqxapi/v1/system/<system_id>/annotations', methods=['POST'])
def add_annotation(system_id):
    uiAPI = UiAPI(app)
    # annotation_name = request.form['mySelect']
    annotation_num = request.form['number']
    return uiAPI.add_annotation(system_id, annotation_num)


# view a system's all annotations
@frontend.route('/aqxapi/v1/system/<system_id>/annotations', methods=['GET'])
def view_annotation(system_id):
    try:
        uiAPI = UiAPI(app)
        return uiAPI.view_annotation(system_id)
    except Exception as ex:
        print "Exception : " + str(ex.message)


# get status by given system uID
@frontend.route('/aqxapi/v1/system/<system_uid>/status', methods=['GET'])
def get_status_by_system_uid(system_uid):
    uiAPI = UiAPI(app)
    return uiAPI.get_status_by_system_uid(system_uid)


# get system id by given system uID
# test purpose
@frontend.route('/aqxapi/v1/system/<user_id>/<name>', methods=['GET'])
def get_system_id_and_system_uid_with_user_id_and_system_name(user_id, name):
    uiAPI = UiAPI(app)
    return uiAPI.get_system_id_and_system_uid_with_user_id_and_system_name(user_id, name)