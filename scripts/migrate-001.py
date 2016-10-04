#!/usr/bin/env python3
"""This is a script to add a measurement type for each
aquaponics system in the database
"""
import MySQLdb
import argparse
from collections import defaultdict

DESCRIPTION = """migrate-001.py - database migration script"""

MEAS_TYPES = {'leaf_count', 'height'}

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=DESCRIPTION)
    parser.add_argument('--dbhost', default="localhost")
    parser.add_argument('--dbuser', default="aquaponics")
    parser.add_argument('--dbpass', default="aquaponics")
    parser.add_argument('--dbname', default="aquaponics")
    args = parser.parse_args()

    conn = MySQLdb.connect(host=args.dbhost, user=args.dbuser,
                           passwd=args.dbpass, db=args.dbname)
    cursor = conn.cursor()
    cursor2 = conn.cursor()
    # query to return all measurement tables
    query = """select table_name from information_schema.tables where table_schema='aquaponics' and table_name like 'aqxs_%'"""

    column_query = """select column_name from information_schema.columns where table_schema='aquaponics' and table_name=%s"""

    try:
        system_meas_types = defaultdict(list)
        cursor.execute(query)
        for row in cursor.fetchall():
            table_name = row[0]
            prefix, meas_type, uid = table_name.split('_')
            system_meas_types[uid].append(meas_type)

            cursor2.execute(column_query, [table_name])
            cols = { r[0] for r in cursor2.fetchall() }
            if 'updated_at' not in cols:
                print('update %s -> %s' % (uid, meas_type))
                update_query1 = """alter table %s add column updated_at timestamp""" % table_name
                update_query2 = """alter table %s add column updated_at timestamp default current_timestamp""" % table_name
                try:
                    cursor2.execute(update_query1)
                except:
                    cursor2.execute(update_query2)

        for uid, meas_types in system_meas_types.items():
            for t in MEAS_TYPES:
                if t not in meas_types:
                    create_query1 = 'CREATE TABLE %s (time TIMESTAMP PRIMARY KEY NOT NULL, value DECIMAL(13,10) NOT NULL, updated_at TIMESTAMP)'
                    create_query2 = 'CREATE TABLE %s (time TIMESTAMP PRIMARY KEY NOT NULL, value DECIMAL(13,10) NOT NULL, updated_at TIMESTAMP default current_timestamp)'
                    table_name = 'aqxs_%s_%s' % (t, uid)
                    print('creating table %s' % table_name)
                    try:
                        cursor.execute(create_query1 % table_name)
                    except:
                        cursor.execute(create_query2 % table_name)

    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()
