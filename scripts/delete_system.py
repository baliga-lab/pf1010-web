#!/usr/bin/env python

"""
Script to delete test systems from your development environment
"""
import MySQLdb
from py2neo import Node, Relationship
import py2neo
import argparse

NEO4J_DELETE_SYSTEM_QUERY = """
MATCH(s:System)
WHERE s.system_id = {system_id}
DETACH DELETE s"""
NEO4J_DELETE_RELATIONSHIP_QUERY = """
MATCH ()-[rel]->(s:System)
WHERE s.system_id={system_id}
DETACH DELETE rel
"""

DESCRIPTION = """delete_system.py - delete the specified system"""

NEO4J_CONNECTION_URI = "http://localhost:7474/db/data/"

def social_graph():
    py2neo.authenticate('localhost', 'neo4j', 'halo32')
    return py2neo.Graph(NEO4J_CONNECTION_URI)

def delete_system_by_system_id(graph, system_id):
    try:
        graph.cypher.execute(NEO4J_DELETE_RELATIONSHIP_QUERY, system_id=system_id)
        graph.cypher.execute(NEO4J_DELETE_SYSTEM_QUERY, system_id=system_id)
        print("deleted in Neo4J (query 1)")
    except:
        graph.run(NEO4J_DELETE_RELATIONSHIP_QUERY, system_id=system_id)
        graph.run(NEO4J_DELETE_SYSTEM_QUERY, system_id=system_id)
        print("deleted in Neo4J (query 2)")

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=DESCRIPTION)
    parser.add_argument('--dbhost', default="localhost")
    parser.add_argument('--dbuser', default="aquaponics")
    parser.add_argument('--dbpass', default="aquaponics")
    parser.add_argument('--dbname', default="aquaponics")
    parser.add_argument('uid')
    args = parser.parse_args()

    conn = MySQLdb.connect(host=args.dbhost, user=args.dbuser,
                           passwd=args.dbpass, db=args.dbname)
    cursor = conn.cursor()
    print "deleting system: %s" % args.uid
    try:
        cursor.execute('select name from measurement_types where id < 10000')
        meas_types = [row[0] for row in cursor.fetchall()]
        cursor.execute('select id,name from systems where system_uid=%s', [args.uid])
        row = cursor.fetchone()
        if row is not None:
            pk, name = row
            cursor.execute('delete from system_notes where system_id=%s', [pk])
            cursor.execute('delete from system_crops where system_id=%s', [pk])
            cursor.execute('delete from system_aquatic_organisms where system_id=%s', [pk])
            cursor.execute('delete from system_gb_media where system_id=%s', [pk])
            cursor.execute('delete from system_annotations where system_id=%s', [pk])
            cursor.execute('delete from system_status where system_uid=%s', [args.uid])
            cursor.execute('delete from systems where id=%s', [pk])
            for meas_type in meas_types:
                try:
                    cursor.execute('drop table aqxs_%s_%s' % (meas_type, args.uid))
                except:
                    pass
            conn.commit()

            # also delete the nodes and relations in Neo4J
            graph = social_graph()
            delete_system_by_system_id(graph, pk)
        else:
            print("system does not exist")
    finally:
        cursor.close()
        conn.close()
