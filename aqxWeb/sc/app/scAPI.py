from aqxWeb.sc.dao.UserDAO import UserDAO
from aqxWeb.sc.dao.SystemDAO import SystemDAO
import json


###############################################################################
# Social Component Data Access API
###############################################################################

class ScAPI:
    # constructor to get connection
    def __init__(self, graph):
        self.graph = graph

    ###############################################################################
    # function : get_logged_in_user
    # purpose : function used to find user based on session(sql_id)
    # params : self
    # returns : User Node json object
    ###############################################################################
    def get_logged_in_user(self):
        user = UserDAO(self.graph).get_logged_in_user()
        if user is not None:
            result = {
                "sql_id": user['sql_id'],
                "google_id": user['google_id'],
                "email": user['email'],
                "givenName": str(user['givenName']),
                "familyName": str(user['familyName']),
                "displayName": str(user['displayName']),
                "gender": str(user['gender']),
                "dob": str(user['dob']),
                "user_type": str(user['user_type']),
                "status": str(user['status'])
            }
            return json.dumps({'user': result})
        else:
            result = {}
            return json.dumps({'user': result})

    ###############################################################################
    # function : get_user_by_google_id
    # purpose : function used to find user based on google_id
    # params : google_id
    # returns : User Node json object
    ###############################################################################
    def get_user_by_google_id(self, google_id):
        user = UserDAO(self.graph).get_user_by_google_id(google_id)
        if user is not None:
            result = {
                "sql_id": user['sql_id'],
                "google_id": user['google_id'],
                "email": user['email'],
                "givenName": str(user['givenName']),
                "familyName": str(user['familyName']),
                "displayName": str(user['displayName']),
                "gender": str(user['gender']),
                "dob": str(user['dob']),
                "user_type": str(user['user_type']),
                "status": str(user['status'])
            }
            return json.dumps({'user': result})
        else:
            result = {}
            return json.dumps({'user': result})

    ###############################################################################
    # function : get_user_by_sql_id
    # purpose : function used to find user based on sql_id
    # params : sql_id
    # returns : User Node json object
    ###############################################################################
    def get_user_by_sql_id(self, sql_id):
        try:
            sql_id = int(sql_id)
            user = UserDAO(self.graph).get_user_by_sql_id(sql_id)
            if user is not None:
                result = {
                    "sql_id": user['sql_id'],
                    "google_id": user['google_id'],
                    "email": user['email'],
                    "givenName": str(user['givenName']),
                    "familyName": str(user['familyName']),
                    "displayName": str(user['displayName']),
                    "gender": str(user['gender']),
                    "dob": str(user['dob']),
                    "user_type": str(user['user_type']),
                    "status": str(user['status'])
                }
                return json.dumps({'user': result})
            else:
                result = {}
                return json.dumps({'user': result})
        except ValueError:
            result = {"status": "sql_id should be integer value. Provided value: " + str(sql_id)}
            return json.dumps({'error': result})

    ###############################################################################
    # function : create_user
    # purpose : function used to create user in the Neo4J database
    # params : User jsonObject
    # returns : Success/Error status
    # Exceptions : General Exception
    ###############################################################################
    def create_user(self, jsonObject):
        try:
            user = jsonObject.get('user')
            if user is not None:
                UserDAO(self.graph).create_user(jsonObject)
                result = {'status': "User Node Successfully Created in Neo4J Database"}
                return json.dumps({'success': result})
            else:
                result = {'status': "Invalid User JSON Object"}
                return json.dumps({'error': result})
        except Exception as e:
            result = {'status': "Exception Occurred While Creating User Node in Neo4J Database: " + str(e)}
            return json.dumps({'error': result})

    ###############################################################################

    # function : delete_user_by_sql_id
    # purpose : function used to delete user in the Neo4J database for the specified sql_id
    # params : sql_id
    # returns : Success/Error status
    # Exceptions : ValueError
    ###############################################################################
    def delete_user_by_sql_id(self, sql_id):
        try:
            sql_id = int(sql_id)
            UserDAO(self.graph).delete_user_by_sql_id(sql_id)
            result = {'status': "User Node Successfully Deleted in Neo4J Database"}
            return json.dumps({'success': result})
        except ValueError:
            result = {"status": "sql_id should be integer value. Provided value: " + str(sql_id)}
            return json.dumps({'error': result})

    ###############################################################################
    # function : create_system
    # purpose : function used to create system node in the Neo4J database
    # params : User jsonObject
    # returns : Success/Error status
    # Exceptions : General Exception
    ###############################################################################
    def create_system(self, jsonObject):
        try:
            sql_id = jsonObject.get('user')
            system = jsonObject.get('system')
            if sql_id is not None and system is not None:
                SystemDAO(self.graph).create_system(jsonObject)
                result = {'status': "System Node Successfully Created in Neo4J Database"}
                return json.dumps({'success': result})
            else:
                result = {'status': "Invalid System JSON Object"}
                return json.dumps({'error': result})
        except Exception as e:
            result = {'status': "Exception Occurred While Creating System Node in Neo4J Database: " + str(e)}
            return json.dumps({'error': result})

    ###############################################################################
    # function : delete_system_by_system_id
    # purpose : function used to delete system in the Neo4J database for the specified system_id
    # params : system_id
    # returns : Success/Error status
    # Exceptions : ValueError
    ###############################################################################
    def delete_system_by_system_id(self, system_id):
        try:
            system_id = int(system_id)
            SystemDAO(self.graph).delete_system_by_system_id(system_id)
            result = {'status': "System Node Successfully Deleted in Neo4J Database"}
            return json.dumps({'success': result})
        except ValueError:
            result = {"status": "system_id should be integer value. Provided value: " + str(system_id)}
            return json.dumps({'error': result})
            ###############################################################################
