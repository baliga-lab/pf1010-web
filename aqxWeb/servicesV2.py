from flask import request, session
from frontend import frontend
from app.APIv2 import API
import MySQLdb

def init_app(flask_app):
    global app
    app = flask_app


def get_conn():
    return MySQLdb.connect(host=app.config['HOST'], user=app.config['USER'],
                           passwd=app.config['PASS'], db=app.config['DB'])


######################################################################
# User Services
######################################################################

# Get userID given googleID
@frontend.route('/aqxapi/v2/user/<googleID>', methods=['GET'])
def getUserID(googleID):
    api = API(app)
    return api.getUserID(googleID)


# Check if user with given googleID exists
@frontend.route('/aqxapi/v2/user/<googleID>/exists', methods=['GET'])
def hasUser(googleID):
    api = API(app)
    return api.hasUser(googleID)


# Create user given google profile then get the userID
@frontend.route('/aqxapi/v2/user', methods=['POST'])
def createUser():
    googleProfile = request.get_json()
    api = API(app)
    return api.createUser(googleProfile)


# Get all systems administrated by user with given userID
@frontend.route('/aqxapi/v2/user/<userID>/system', methods=['GET'])
def getSystemsForUser(userID):
    api = API(app)
    return api.getSystemsForUser(userID)


# Delete user with given userID
@frontend.route('/aqxapi/v2/user/<userID>', methods=['DELETE'])
def deleteUser(userID):
    api = API(app)
    return api.deleteUser(userID)


######################################################################
# System Services
######################################################################

# Get metadata info for a system with given systemUID
@frontend.route('/aqxapi/v2/system/<systemUID>', methods=['GET'])
def getSystem(systemUID):
    api = API(app)
    return api.getSystem(systemUID)


# Create a new system whose administrator is the current logged in user
@frontend.route('/aqxapi/v2/system', methods=['POST'])
def createSystem():
    api = API(app)
    system = request.get_json()
    system['userID'] = session['uid']
    return api.createSystem(system)


# Delete a system with the given systemUID
@frontend.route('/aqxapi/v2/system/<systemUID>', methods=['DELETE'])
def deleteSystem(systemUID):
    api = API(app)
    return api.deleteSystem(systemUID)


# Get annotations for a system with given systemID
@frontend.route('/aqxapi/v2/system/<systemID>/annotation', methods=['GET'])
def getAnnotationsForSystem(systemID):
    api = API(app)
    return api.getAnnotationsForSystem(systemID)


# Add an annotation for system with given systemID
@frontend.route('/aqxapi/v2/system/<systemID>/annotation', methods=['POST'])
def addAnnotation(systemID):
    api = API(app)
    annotation = request.get_json()
    annotation['systemID'] = systemID
    return api.addAnnotation(annotation)


# Get latest reading of a system with given systemUID for each measurement type
@frontend.route('/aqxapi/v2/system/<systemUID>/reading', methods=['GET'])
def getLatestReadingsForSystem(systemUID):
    api = API(app)
    return api.getLatestReadingsForSystem(systemUID)


# Submit reading for given measurementType for system with given systemUID
@frontend.route('/aqxapi/v2/system/<systemUID>/reading/<measurementType>', methods=['POST'])
def submitReading(systemUID, measurementType):
    api = API(app)
    reading = request.get_json()
    return api.submitReading(measurementType, systemUID, reading)


######################################################################
# Metadata Services
######################################################################

# Get enums which might be useful for populating options
@frontend.route('/aqxapi/v2/enums', methods=['GET'])
def getEnums():
    api = API(app)
    return api.getEnums()


######################################################################
# Subscription Services
######################################################################

# Subscribe the given email to the mailing list
@frontend.route('/aqxapi/v2/mailing', methods=['POST'])
def subscribe():
    api = API(app)
    email = request.get_json()['email']
    return api.subscribe(email)


######################################################################
# Annotation Services
######################################################################

# Get (somewhat) readable annotation given annotationID
@frontend.route('/aqxapi/v2/annotation/<annotationID>', methods=['GET'])
def getReadableAnnotation(annotationID):
    api = API(app)
    return api.getReadableAnnotation(annotationID)


# Get (somewhat) readable annotations map
@frontend.route('/aqxapi/v2/annotation', methods=['GET'])
def getReadableAnnotations():
    api = API(app)
    return api.getReadableAnnotations()
