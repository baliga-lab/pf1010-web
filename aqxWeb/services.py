from flask import request, session, current_app, jsonify
from frontend import frontend
from api import API
from datetime import datetime
import time
import json

# to connect system to the social system
from aqxWeb.social.models import social_graph
from aqxWeb.social.api import SocialAPI


# Expected format to arrive from the client
UI_DATE_FORMAT = '%Y-%m-%d'

def parse_date(s):
    try:
        return datetime.fromtimestamp(time.mktime(time.strptime(s, UI_DATE_FORMAT)))
    except:
        current_app.logger.warn("problem using default date format, none returned, input was: %s" % s)
        return None

######################################################################
# User Services
######################################################################

# Get userID given googleID
@frontend.route('/aqxapi/v2/user/<googleID>', methods=['GET'])
def getUserID(googleID):
    api = API(current_app)
    return api.getUserID(googleID)


# Check if user with given googleID exists
@frontend.route('/aqxapi/v2/user/<googleID>/exists', methods=['GET'])
def hasUser(googleID):
    api = API(current_app)
    return api.hasUser(googleID)


# Create user given google profile then get the userID
@frontend.route('/aqxapi/v2/user', methods=['POST'])
def createUser():
    googleProfile = request.get_json()
    api = API(current_app)
    return api.createUser(googleProfile)


# Get all systems administrated by user with given userID
@frontend.route('/aqxapi/v2/user/<userID>/system', methods=['GET'])
def getSystemsForUser(userID):
    api = API(current_app)
    return api.getSystemsForUser(userID)


######################################################################
# System Services
######################################################################

# Get metadata info for a system with given systemUID
@frontend.route('/aqxapi/v2/system/<systemUID>', methods=['GET'])
def get_system(systemUID):
    return json.dumps(API(current_app).get_system(systemUID))


SYSTEM_INITIAL_STATUS = 100


@frontend.route('/aqxapi/v2/system', methods=['POST'])
def api_create_system():
    """Create a new system whose administrator is the current logged in user"""
    api = API(current_app)
    system = request.get_json()
    system['userID'] = session['uid']
    system['startDate'] = parse_date(system['startDate'])
    system['status'] = SYSTEM_INITIAL_STATUS
    system_id = 0
    system_uid = ''

    if system['startDate'] is None:
        return json.dumps({'error': 'error in start date format'})

    try:
        sys_data = api.create_system(system)
    except Exception as e:
        current_app.logger.exception('could not create system')
        return json.dumps({'error': 'database error while creating system'})

    # create social link here
    social_obj = {
        'user': session['uid'],
        'system': {
            'system_id': sys_data['systemID'],
            'system_uid': sys_data['systemUID'],
            'name': system['name'],
            'description': system['name'],
            'location_lat': system['location']['lat'],
            'location_lng': system['location']['lng'],
            'status': SYSTEM_INITIAL_STATUS
        }
    }
    result = SocialAPI(social_graph()).create_system(social_obj)
    if 'success' in result:
        return json.dumps(sys_data)
    else:
        return json.dumps(result)


# Get annotations for a system with given systemID
@frontend.route('/aqxapi/v2/system/<systemID>/annotation', methods=['GET'])
def getAnnotationsForSystem(systemID):
    api = API(current_app)
    return api.getAnnotationsForSystem(systemID)


"""
# Add an annotation for system with given systemID
@frontend.route('/aqxapi/v2/system/<systemID>/annotation', methods=['POST'])
def addAnnotation(systemID):
    api = API(current_app)
    annotation = request.get_json()
    annotation['systemID'] = systemID
    return api.addAnnotation(annotation)
"""

@frontend.route('/aqxapi/v2/measurement_types', methods=['GET'])
def measurement_types():
    api = API(current_app)
    return api.measurement_types()

######################################################################
# Subscription Services
######################################################################

# Subscribe the given email to the mailing list
@frontend.route('/aqxapi/v2/mailing', methods=['POST'])
def subscribe():
    api = API(current_app)
    email = request.get_json()['email']
    return api.subscribe(email)


######################################################################
# Annotation Services
######################################################################

# Get (somewhat) readable annotation given annotationID
@frontend.route('/aqxapi/v2/annotation/<annotationID>', methods=['GET'])
def getReadableAnnotation(annotationID):
    api = API(current_app)
    return api.getReadableAnnotation(annotationID)


# Get (somewhat) readable annotations map
@frontend.route('/aqxapi/v2/annotation', methods=['GET'])
def getReadableAnnotations():
    api = API(current_app)
    return api.getReadableAnnotations()
