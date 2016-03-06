from aqxWeb.sc.dao.UserDAO import UserDAO
import json


# Social Component Data Access API


class ScAPI:
    # constructor to get connection
    def __init__(self, graph):
        self.graph = graph

    ###############################################################################
    # function : get_logged_in_user
    # purpose : function used to find user based on session(sql_id)
    # params : self
    # returns : User Node json object
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
            result = {"error": "sql_id should be integer value. Provided value: " + sql_id}
            return json.dumps({'user': result})
