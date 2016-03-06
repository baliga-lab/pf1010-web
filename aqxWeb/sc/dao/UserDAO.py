from py2neo import Node, cypher
from flask import session
from aqxWeb.sc.models import timestamp
import json


# DAO for User Node in the Neo4J database
class UserDAO:
    # constructor to get connection
    def __init__(self, graph):
        self.graph = graph

    ###############################################################################
    # function : get_logged_in_user
    # purpose : function used to find user based on session(sql_id)
    # params : self
    # returns : User node
    # Exceptions : cypher.CypherError, cypher.CypherTransactionError
    def get_logged_in_user(self):
        try:
            if session.get('uid') is not None:
                user = self.graph.find_one("User", "sql_id", session.get('uid'))
                return user
        except cypher.CypherError, cypher.CypherTransactionError:
            raise "Exception occured in function get_logged_in_user"

    ###############################################################################
    # function : get_user_by_google_id
    # purpose : function used to find user based on google_id
    # params : self, google_id
    # returns : User node
    # Exceptions : cypher.CypherError, cypher.CypherTransactionError
    def get_user_by_google_id(self, google_id):
        try:
            user = self.graph.find_one("User", "google_id", google_id)
            return user
        except cypher.CypherError, cypher.CypherTransactionError:
            raise "Exception occured in function get_user_by_google_id"

    ###############################################################################

    ###############################################################################
    # function : get_user_by_sql_id
    # purpose : function used to find user based on sql_id
    # params : self, sql_id
    # returns : User node
    # Exceptions : cypher.CypherError, cypher.CypherTransactionError
    def get_user_by_sql_id(self, sql_id):
        try:
            user = self.graph.find_one("User", "sql_id", int(sql_id))
            return user
        except cypher.CypherError, cypher.CypherTransactionError:
            raise "Exception occured in function get_user_by_sql_id"

    ###############################################################################


    ###############################################################################
    # function : _user_by_sql_id
    # purpose : function used to delete the user from Neo4J Database based on sql_id
    # params : self, sql_id
    # returns : None
    # Exceptions : cypher.CypherError, cypher.CypherTransactionError
    def create_user(self, jsonObject):
        try:
            user = jsonObject.get('user')
            sql_id = user.get('sql_id')
            sql_id = int(sql_id)
            is_user_existing = self.graph.find_one("User", "sql_id", sql_id)
            # Create User node in the Neo4J database, only when there is no existing user with the provided sql_id
            if is_user_existing is None:
                google_id = user.get('google_id')
                email = user.get('email')
                givenName = user.get('givenName')
                familyName = user.get('familyName')
                displayName = user.get('displayName')
                user_type = user.get('user_type')
                organization = user.get('organization')
                dob = user.get('dob')
                gender = user.get('gender')
                status = user.get('status')
                userNode = Node("User", sql_id=sql_id, google_id=google_id, email=email, givenName=givenName,
                                familyName=familyName, displayName=displayName, user_type=user_type,
                                organization=organization, creation_time=timestamp(), modified_time=timestamp(),
                                dob=dob, gender=gender, status=status)
                self.graph.create(userNode)
        except cypher.CypherError, cypher.CypherTransactionError:
            raise "Exception occured in function create_user"

    ###############################################################################

    ###############################################################################
    # function : delete_user_by_sql_id
    # purpose : function used to delete the user from Neo4J Database based on sql_id
    # params : self, sql_id
    # returns : None
    # Exceptions : cypher.CypherError, cypher.CypherTransactionError
    def delete_user_by_sql_id(self, sql_id):
        try:
            user = self.graph.find_one("User", "sql_id", sql_id)
            self.graph.delete(user)
        except cypher.CypherError, cypher.CypherTransactionError:
            raise "Exception occured in function delete_user_by_sql_id"

            ###############################################################################
