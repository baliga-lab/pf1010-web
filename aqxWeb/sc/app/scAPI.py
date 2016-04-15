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
        if user is None:
            result = {}
            return json.dumps({'user': result})
        elif 'error' in user:
            return user
        else:
            result = {
                "sql_id": user['sql_id'],
                "google_id": user['google_id'],
                "email": user['email'],
                "givenName": str(user['givenName']),
                "familyName": str(user['familyName']),
                "displayName": str(user['displayName']),
                "gender": str(user['gender']),
                "dob": str(user['dob']),
                "image_url": str(user['image_url']),
                "user_type": str(user['user_type']),
                "status": user['status']
            }
            return json.dumps({'user': result})

    ###############################################################################
    # function : get_user_by_google_id
    # purpose : function used to find user based on google_id
    # params : google_id
    # returns : User Node json object
    ###############################################################################
    def get_user_by_google_id(self, google_id):
        user = UserDAO(self.graph).get_user_by_google_id(google_id)
        if user is None:
            result = {}
            return json.dumps({'user': result})
        elif 'error' in user:
            return user
        else:
            result = {
                "sql_id": user['sql_id'],
                "google_id": user['google_id'],
                "email": user['email'],
                "givenName": str(user['givenName']),
                "familyName": str(user['familyName']),
                "displayName": str(user['displayName']),
                "gender": str(user['gender']),
                "dob": str(user['dob']),
                "image_url": str(user['image_url']),
                "user_type": str(user['user_type']),
                "status": user['status']
            }
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
            if user is None:
                result = {}
                return json.dumps({'user': result})
            elif 'error' in user:
                return user
            else:
                result = {
                    "sql_id": user['sql_id'],
                    "google_id": user['google_id'],
                    "email": user['email'],
                    "givenName": str(user['givenName']),
                    "familyName": str(user['familyName']),
                    "displayName": str(user['displayName']),
                    "gender": str(user['gender']),
                    "dob": str(user['dob']),
                    "image_url": str(user['image_url']),
                    "user_type": str(user['user_type']),
                    "status": user['status']
                }
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
                result = UserDAO(self.graph).create_user(jsonObject)
                return result
            else:
                error_msg = json.dumps({'error': "Invalid User JSON Object"})
                return error_msg
        except Exception as ex:
            error_msg = json.dumps(
                {'error': "Exception Occurred While Creating User Node in Neo4J Database: " + str(ex.message)})
            return error_msg

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
            result = UserDAO(self.graph).delete_user_by_sql_id(sql_id)
            return result
        except ValueError:
            error_msg = json.dumps({"error": "sql_id should be integer value. Provided value: " + str(sql_id)})
            return error_msg

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
                result = SystemDAO(self.graph).create_system(jsonObject)
                return result
            else:
                error_msg = json.dumps({'error': "Invalid System JSON Object"})
                return error_msg
        except Exception as ex:
            error_msg = json.dumps(
                {'error': "Exception Occurred While Creating System Node in Neo4J Database: " + str(ex.message)})
            return error_msg

    ###############################################################################
    # function : update_system_with_system_uid
    # purpose : function used to update system node in the Neo4J database
    # params : User jsonObject
    # returns : Success/Error status
    # Exceptions : General Exception
    ###############################################################################
    def update_system_with_system_uid(self, jsonObject):
        try:
            system = jsonObject.get('system')
            if system is not None:
                result = SystemDAO(self.graph).update_system_with_system_uid(jsonObject)
                return result
            else:
                error_msg = json.dumps({'error': "Invalid System JSON Object"})
                return error_msg
        except Exception as ex:
            error_msg = json.dumps(
                {'error': "Exception Occurred While Updating System Node in Neo4J Database: " + str(ex.message)})
            return error_msg

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
            result = SystemDAO(self.graph).delete_system_by_system_id(system_id)
            return result
        except ValueError:
            error_msg = json.dumps({"error": "system_id should be integer value. Provided value: " + str(system_id)})
            return error_msg

    ###############################################################################
    # function : get_system_for_user
    # purpose : function to return the systems from Neo4J database where the user is related to
    # params : self, sql_id
    # returns : Success/Error status
    # Exceptions : ValueError
    ###############################################################################
    def get_system_for_user(self, sql_id):
        try:
            sql_id = int(sql_id)
            system_results = SystemDAO(self.graph).get_system_for_user(sql_id)
            if 'error' in system_results:
                return system_results
            else:
                if system_results is not None:
                    systems_list = []
                    for system in system_results:
                        result = {
                            "system_id": system[0]['system_id'],
                            "system_uid": system[0]['system_uid'],
                            "name": system[0]['name'],
                            "description": system[0]['description'],
                            "creation_time": system[0]['creation_time'],
                            "modified_time": system[0]['modified_time'],
                            "status": system[0]['status']
                        }
                        systems_list.append(result)
                    result = json.dumps({'system': systems_list})
                    return result
                else:
                    result = json.dumps({'system': {}})
                    return result
        except ValueError:
            error_msg = json.dumps({"error": "sql_id should be integer value. Provided value: " + str(sql_id)})
            return error_msg
            ###############################################################################
