from py2neo import Graph, Node, Relationship, cypher
from flask import session


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
