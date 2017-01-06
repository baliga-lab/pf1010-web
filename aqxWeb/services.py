from flask import request, session, current_app
from frontend import frontend
from api import API
from datetime import datetime
import time


# Expected format to arrive from the client
# the second format handles milliseconds
API_TIME_FORMAT1 = '%Y-%m-%dT%H:%M:%SZ'
API_TIME_FORMAT2 = '%Y-%m-%dT%H:%M:%S.%fZ'
"""2016-07-15T00:00:00.000Z"""
def parse_timestamp(s):
    try:
        return datetime.fromtimestamp(time.mktime(time.strptime(s, API_TIME_FORMAT1)))
    except:
        try:
            return datetime.fromtimestamp(time.mktime(time.strptime(s, API_TIME_FORMAT2)))
        except:
            current_app.logger.warn("problem using API default format, none returned, input was: %s" % s)
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


# Delete user with given userID
@frontend.route('/aqxapi/v2/user/<userID>', methods=['DELETE'])
def deleteUser(userID):
    api = API(current_app)
    return api.deleteUser(userID)


######################################################################
# System Services
######################################################################

# Get metadata info for a system with given systemUID
@frontend.route('/aqxapi/v2/system/<systemUID>', methods=['GET'])
def getSystem(systemUID):
    api = API(current_app)
    return api.getSystem(systemUID)


@frontend.route('/aqxapi/v2/system', methods=['POST'])
def api_create_system():
    """Create a new system whose administrator is the current logged in user"""
    api = API(current_app)
    system = request.get_json()
    system['userID'] = session['uid']
    system['startDate'] = parse_timestamp(system['startDate'])
    return api.create_system(system)


# Delete a system with the given systemUID
@frontend.route('/aqxapi/v2/system/<systemUID>', methods=['DELETE'])
def deleteSystem(systemUID):
    api = API(current_app)
    return api.deleteSystem(systemUID)


# Get annotations for a system with given systemID
@frontend.route('/aqxapi/v2/system/<systemID>/annotation', methods=['GET'])
def getAnnotationsForSystem(systemID):
    api = API(current_app)
    return api.getAnnotationsForSystem(systemID)


# Add an annotation for system with given systemID
@frontend.route('/aqxapi/v2/system/<systemID>/annotation', methods=['POST'])
def addAnnotation(systemID):
    api = API(current_app)
    annotation = request.get_json()
    annotation['systemID'] = systemID
    return api.addAnnotation(annotation)


# Get latest reading of a system with given systemUID for each measurement type
@frontend.route('/aqxapi/v2/system/<systemUID>/reading', methods=['GET'])
def latest_readings_for_system(systemUID):
    api = API(current_app)
    return api.latest_readings_for_system(systemUID)


# Submit reading for given measurementType for system with given systemUID
@frontend.route('/aqxapi/v2/system/<systemUID>/reading/<measurementType>', methods=['POST'])
def submit_reading(systemUID, measurementType):
    api = API(current_app)
    reading = request.get_json()
    return api.submit_reading(measurementType, systemUID, reading)

@frontend.route('/aqxapi/v2/measurement_types', methods=['GET'])
def measurement_types():
    api = API(current_app)
    return api.measurement_types()


######################################################################
# Metadata Services
######################################################################

# Get enums which might be useful for populating options
@frontend.route('/aqxapi/v2/enums', methods=['GET'])
def getEnums():
    api = API(current_app)
    return api.getEnums()


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
