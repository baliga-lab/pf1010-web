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
    # Exceptions : Exception
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
                status = system.get('status')
                systemNode = Node("System", system_id=system_id, system_uid=system_uid, name=name,
                                  description=description, status=status,
                                  creation_time=timestamp(), modified_time=timestamp())
                self.graph.create(systemNode)
                relationship = Relationship(is_existing_user, "SYS_ADMIN", systemNode)
                self.graph.create(relationship)
        except Exception as e:
            raise "Exception occured in function create_system " + str(e)

    ###############################################################################
    # function : update_system_with_system_uid
    # purpose : function used to update System node in the Neo4J Database
    # params : self, system JSON Object
    # returns : None
    # Exceptions : Exception
    def update_system_with_system_uid(self, jsonObject):
        try:
            system = jsonObject.get('system')
            system_uid = system.get('system_uid')
            is_existing_system = self.graph.find_one("System", "system_uid", system_uid)
            # Create System node in the Neo4J database, only when there is no system with the provided system_id
            if is_existing_system is not None:
                name = system.get('name')
                description = system.get('description')
                status = system.get('status')
                update_system_query = """
                MATCH(s:System)
                WHERE s.system_uid = {system_uid}
                SET s.name = {name}, s.description = {description},
                s.status = {status}, s.modified_time = {modified_time}
                """
                self.graph.cypher.execute(update_system_query, system_uid=system_uid, name=name,
                                          description=description, status=status,
                                          modified_time=timestamp())
        except Exception as e:
            raise "Exception occured in function update_system_with_system_uid " + str(e)

    ###############################################################################
    # function : delete_system_by_system_id
    # purpose : function used to delete the system from Neo4J Database based on system_id
    # params : self, system_id
    # returns : None
    # Exceptions : Exception
    def delete_system_by_system_id(self, system_id):
        try:
            system = self.graph.find_one("System", "system_id", system_id)
            self.graph.delete(system)
        # except cypher.CypherError, cypher.CypherTransactionError:
        except Exception as e:
            raise "Exception occured in function delete_system_by_system_id " + str(e)

            ###############################################################################


    ###############################################################################
    # function : get_system_for_user
    # purpose : function to return the systems from Neo4J database where the user is related to
    # params : self, sql_id
    # returns : None
    # Exceptions : Exception
    def get_system_for_user(self, sql_id):
        try:
            query = """
            MATCH (u:User)-[rel]-(s:System)
            WHERE u.sql_id = {sql_id} and
            NOT (type(rel) = "SYS_PENDING_PARTICIPANT")
            RETURN s
            ORDER BY s.name
            """
            system = self.graph.cypher.execute(query, sql_id = sql_id);
            return system
        except Exception as e:
            raise "Exception occured in function get_system_for_user " + str(e)

    ###############################################################################