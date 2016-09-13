#!/usr/bin/env python3
"""
link_legacy_systems.py - a tool to link systems in MySQL to systems.

A systems node in Neo4j has
  - system_id (PK from MySQL)
  - system_uid
  - creation_time (a timestamp represented by a large integer)
  - modified_time (a timestamp represented by a large integer)
  - location_lng
  - location_lat
  - name
  - description
  - status

From the standpoint of the data this is currently a catastrophe:
  - information from the relational database is duplicated
    in the social graph, with a high potential risk for consistency
"""
import time
import py2neo
import argparse
import MySQLdb
import traceback as tb


def timestamp():
    """copied from models, to break cyclic dependency"""
    return int(round(time.time() * 1000))


def social_graph(settings):
    try:
        py2neo.authenticate(settings['NEO4J_HOST'],
                            settings['NEO4J_USER'],
                            settings['NEO4J_PASS'])
        return py2neo.Graph(settings['NEO4J_CONNECTION_URI'])
    except Exception as ex:
        current_app.logger.exception("Exception At init_sc_app: ", ex)
        raise


def graph_update(settings, query, **kwargs):
    """py2neo has significant changes in the API between V2 and V3,
    this function tries to be compatible to both APIs"""
    try:
        return social_graph(settings).cypher.execute(query, kwargs)
    except Exception as e:
        cursor = social_graph(settings).run(query, kwargs)
        return [r for r in cursor]


def graph_query(settings, query, **kwargs):
    try:
        return social_graph(settings).cypher.execute(query, kwargs)
    except:
        cursor = social_graph(settings).run(query, kwargs)
        return [r for r in cursor]

def dbconn(settings):
    return MySQLdb.connect(host=settings['HOST'], user=settings['USER'],
                            passwd=settings['PASS'], db=settings['DB'])


def read_settings(path):
    global_vars = {}
    local_vars = {}
    try:
        execfile(args.config_file, global_vars, local_vars)
    except:
        with open(args.config_file) as infile:
            code = compile(infile.read(), args.config_file, 'exec')
            exec(code, global_vars, local_vars)
    return local_vars


def user_systems(conn, user_id):
    """Find all the legacy system UIDs for the specified user"""
    cursor = conn.cursor()
    try:
        cursor.execute('select system_uid from systems where user_id=%s', [user_id])
        return [row[0] for row in cursor.fetchall()]
    finally:
        if cursor is not None:
            cursor.close()


def not_in_graph(uids):
    """Determine the system uids that need to be created in the system"""
    system_query = """MATCH (system:System)
    where system.system_uid IN {system_uid_collection}
    return system
    ORDER By system.name"""
    result = graph_query(settings, system_query, system_uid_collection=uids)
    graph_uids = set([entry['system']['system_uid'] for entry in result])
    return [uid for uid in uids if uid not in graph_uids]

def systems_data_for(conn, uids):
    """returns the data required to create a System node"""
    query = """select id,system_uid,creation_time,location_lng,location_lat,name,status,user_id
             from systems where system_uid in %s"""
    cursor = conn.cursor()
    try:
        cursor.execute(query, [uids])
        result = []
        for row in cursor.fetchall():
            # if system has no location, retrieve from user default site
            if row[3] is None or row[4] is None:
                cursor2 = conn.cursor()
                cursor2.execute('select default_site_location_lat,default_site_location_lng from users where id=%s', [row[7]])
                lat, lng = cursor2.fetchone()
            else:
                lat = row[4]
                lng = row[3]

            result.append({'id': row[0], 'system_uid': row[1], 'creation_time': row[2],
                            'location_lng': lng, 'location_lat': lat, 'name': row[5],
                            'status': row[6]})
        return result
    finally:
        if cursor is not None:
            cursor.close()

def to_float(value):
    if value is not None:
        return float(value)
    else:
        return 0.0

def make_systems_in_graph(settings, user_id, system_data):
    graph = social_graph(settings)
    system_owner = graph.find_one("User", "sql_id", user_id)
    if system_owner is None:
        print("user is not in graph yet (never logged in), skipping")
        return
    for entry in system_data:
        print(entry)
        try:
            systemNode = py2neo.Node("System",
                                         system_id=entry['id'],
                                         system_uid=entry['system_uid'],
                                         name=entry['name'],
                                         description=entry['name'],
                                         location_lat=to_float(entry['location_lat']),
                                         location_lng=to_float(entry['location_lng']),
                                         status=entry['status'],
                                         creation_time=timestamp(),
                                         modified_time=timestamp())
            graph.create(systemNode)
            relationship = py2neo.Relationship(system_owner, "SYS_ADMIN", systemNode)
            graph.create(relationship)
        except Exception as e:
            tb.print_exc()
            raise e

def process_user(settings, conn, user_id, email):
    print("processing systems for user: %s" % email)
    system_uids = user_systems(conn, user_id)
    uids_to_add = not_in_graph(system_uids)
    if len(uids_to_add) > 0:
        print("# of systems to add: %d" % len(uids_to_add))
        systems_data = systems_data_for(conn, uids_to_add)
        make_systems_in_graph(settings, user_id, systems_data)
    else:
        print('nothing to be done, skipping.')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="link_legacy_sytems.py - connect systems to their users")
    parser.add_argument('config_file')
    parser.add_argument('--user_id', type=int, default=None)
    args = parser.parse_args()
    settings = read_settings(args.config_file)
    graph = social_graph(settings)
    conn = dbconn(settings)
    try:
        cursor = conn.cursor()
        if args.user_id is None:
            cursor.execute('select distinct id, email from users')
            for user_id, email in cursor.fetchall():
                process_user(settings, conn, user_id, email)
        else:
            cursor.execute('select email from users where id=%s', [args.user_id])
            process_user(settings, conn, args.user_id, cursor.fetchone()[0])
    finally:
        conn.close()
