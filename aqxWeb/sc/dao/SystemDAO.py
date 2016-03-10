from py2neo import Node, cypher, Relationship
from flask import session
from aqxWeb.sc.models import timestamp


# DAO for System Node in the Neo4J database
class SystemDAO:
    # constructor to get connection
    def __init__(self, graph):
        self.graph = graph

    ###############################################################################
    # function : create_system
    # purpose : function used to create System node in the Neo4J Database
    # params : self, system JSON Object
    # returns : None
    # Exceptions : cypher.CypherError, cypher.CypherTransactionError
    def create_system(self, jsonObject):
        try:
            sql_id = jsonObject.get('user')
            sql_id = int(sql_id)
            system = jsonObject.get('system')
            system_id = system.get('system_id')
            system_id = int(system_id)
            is_existing_user = self.graph.find_one("User", "sql_id", sql_id)
            is_existing_system = self.graph.find_one("System", "system_id", system_id)
            # Create System node in the Neo4J database, only when there is no system with the provided system_id
            # Also the user node should exists in the Neo4J database
            if is_existing_user is not None and is_existing_system is None:
                system_uid = system.get('system_uid')
                name = system.get('name')
                description = system.get('description')
                systemNode = Node("System", system_id=system_id, system_uid=system_uid, name=name,
                                  description=description,
                                  creation_time=timestamp(), modified_time=timestamp())
                self.graph.create(systemNode)
                relationship = Relationship(is_existing_user, "SYS_ADMIN", systemNode)
                self.graph.create(relationship)
        except cypher.CypherError, cypher.CypherTransactionError:
            raise "Exception occured in function create_system"

    ###############################################################################
    # function : delete_system_by_system_id
    # purpose : function used to delete the system from Neo4J Database based on system_id
    # params : self, system_id
    # returns : None
    # Exceptions : cypher.CypherError, cypher.CypherTransactionError
    def delete_system_by_system_id(self, system_id):
        try:
            system = self.graph.find_one("System", "system_id", system_id)
            self.graph.delete(system)
        except cypher.CypherError, cypher.CypherTransactionError:
            raise "Exception occured in function delete_system_by_system_id"

            ###############################################################################
