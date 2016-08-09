import json
from py2neo import Node, cypher
from flask import session
from aqxWeb.sc.models import timestamp


# DAO for User Node in the Neo4J database
class UserDAO:
    # constructor to set connection
    def __init__(self, graph):
        self.graph = graph

    ###############################################################################
    # function : get_logged_in_user
    # purpose : function used to find user based on session(sql_id)
    # params : self
    # returns : User node
    # Exceptions : General Exception
    def get_logged_in_user(self):
        try:
            if session.get('uid') is not None:
                user = self.graph.find_one("User", "sql_id", session.get('uid'))
                return user
            else:
                error_msg = json.dumps({'error': 'User has to login the website to get his/her profile details'})
                return error_msg
        except Exception as ex:
            error_msg = json.dumps({'error': 'Exception Occurred At get_logged_in_user: ' + str(ex.message)})
            return error_msg

    ###############################################################################
    # function : get_user_by_google_id
    # purpose : function used to find user based on google_id
    # params : self, google_id
    # returns : User node
    # Exceptions : General Exception
    def get_user_by_google_id(self, google_id):
        try:
            user = self.graph.find_one("User", "google_id", google_id)
            return user
        except Exception as ex:
            error_msg = json.dumps({'error': 'Exception Occurred At get_user_by_google_id: ' + str(ex.message)})
            return error_msg

    ###############################################################################
    # function : get_user_by_sql_id
    # purpose : function used to find user based on sql_id
    # params : self, sql_id
    # returns : User node
    # Exceptions : General Exception
    def get_user_by_sql_id(self, sql_id):
        try:
            user = self.graph.find_one("User", "sql_id", int(sql_id))
            return user
        except Exception as ex:
            error_msg = json.dumps({'error': 'Exception Occurred At get_user_by_sql_id: ' + str(ex.message)})
            return error_msg

    ###############################################################################
    # function : create_user
    # purpose : function used to create the user node in Neo4J Database
    # params : self, user JSON Object
    # returns : None
    # Exceptions : General Exception
    def create_user(self, jsonObject):
        try:
            user = jsonObject.get('user')
            sql_id = user.get('sql_id')
            sql_id = int(sql_id)
            is_existing_user = self.graph.find_one("User", "sql_id", sql_id)
            # Create User node in the Neo4J database, only when there is no user with the provided sql_id
            if is_existing_user is None:
                google_id = user.get('google_id')
                email = user.get('email')
                givenName = user.get('givenName')
                familyName = user.get('familyName')
                displayName = user.get('displayName')
                user_type = user.get('user_type')
                image_url = user.get('image_url')
                organization = user.get('organization')
                dob = user.get('dob')
                gender = user.get('gender')
                status = user.get('status')
                userNode = Node("User", sql_id=sql_id, google_id=google_id, email=email, givenName=givenName,
                                familyName=familyName, displayName=displayName, user_type=user_type,
                                image_url=image_url,
                                organization=organization, creation_time=timestamp(), modified_time=timestamp(),
                                dob=dob, gender=gender, status=status)
                self.graph.create(userNode)
                result = json.dumps({'success': "User Node Successfully Created in Neo4J Database"})
                return result
            else:
                result = json.dumps({'error': "User Node Already Exists In Neo4J Database. " + jsonObject})
                return result
        except Exception as ex:
            error_msg = json.dumps({'error': 'Exception Occurred At create_user: ' + str(ex.message)})
            return error_msg

    ###############################################################################
    # function : delete_user_by_sql_id
    # purpose : function used to delete the user from Neo4J Database based on sql_id
    # params : self, sql_id
    # returns : None
    # Exceptions : General Exception
    def delete_user_by_sql_id(self, sql_id):
        try:
            delete_user_query = """
            MATCH(u:User)
            WHERE u.sql_id = {sql_id}
            DETACH DELETE u
            """
            self.graph.cypher.execute(delete_user_query, sql_id=sql_id)
            result = json.dumps({'success': "User Node Successfully Deleted in Neo4J Database"})
            return result
        except Exception as ex:
            error_msg = json.dumps({'error': 'Exception Occurred At delete_user_by_sql_id: ' + str(ex.message)})
            return error_msg

    ###############################################################################

    # function : get_unblocked_friends_by_sql_id
    # purpose : function used to find unblocked friends based on sql_id of the user
    # params : self, sql_id
    # returns : User node
    # Exceptions : cypher.CypherError, cypher.CypherTransactionError
    def get_unblocked_friends_by_sql_id(self, sql_id):
        my_sql_id = sql_id
        query = """
            MATCH (n:User)-[r:FRIENDS]-(n1:User)
            WHERE n1.sql_id = {sql_id} and r.blocker_id = {blocker_id}
            return n
            ORDER BY n.givenName
        """

        try:
            friendlist = self.graph.cypher.execute(query, sql_id=my_sql_id, blocker_id="");
            return friendlist
        except cypher.CypherError, cypher.CypherTransactionError:
            raise "Exception occured in function get_unblocked_friends_by_sql_id"

            ###############################################################################

            ###############################################################################

    # function : get_blocked_friends_by_sql_id
    # purpose : function used to find blocked friends based on sql_id of the user
    # params : self, sql_id
    # returns : User node
    # Exceptions : cypher.CypherError, cypher.CypherTransactionError
    def get_blocked_friends_by_sql_id(self, sql_id):
        my_sql_id = sql_id

        query = """
            MATCH (n:User)-[r:FRIENDS]-(n1:User)
            WHERE n1.sql_id = {sql_id} and r.blocker_id = {blocker_id}
            return n
            ORDER BY n.givenName
        """

        try:
            friendlist = self.graph.cypher.execute(query, sql_id=my_sql_id, blocker_id=my_sql_id);
            return friendlist
        except cypher.CypherError, cypher.CypherTransactionError:
            raise "Exception occured in function get_blocked_friends_by_sql_id"

            ###############################################################################
