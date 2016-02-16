from py2neo import authenticate,Graph, Node, Relationship
from neo4jrestclient.client import GraphDatabase

authenticate("localhost:7474", "neo4j", "neo4jnew")
graph = Graph()

class User:

    def __init__(self, firstname, lastname, dateofbirth, organization, email):
        self.db = GraphDatabase("http://localhost:7474", username="neo4j", password="neo4jnew")
        self.firstname = firstname
        self.lastname = lastname
        self.dateofbirth = dateofbirth
        self.organization = organization
        self.email = email

    def find(self):
        user_returned = graph.find_one("Users", "name", "Venkatesh")
        return user_returned

    def updateprofile(self):
        user_to_update = self.find()
        query = """
        MATCH(x:Users)
        WHERE x.sql_id = 1
        SET x.name = {nameupdate}
        """

        return graph.cypher.execute(query, nameupdate=self.firstname)



