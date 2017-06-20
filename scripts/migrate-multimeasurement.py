#!/usr/bin/env python
import MySQLdb
import argparse

DESCRIPTION = """migrate-multimeasurement.py - migrate to multi-measurement tables"""
BROKEN_SYSTEMS = set()

def get_default_crops(cursor, system_pk, system_uid):
    cursor.execute('select crop_id from system_crops where system_id=%s', (system_pk, ))
    row = cursor.fetchone()
    if row is None:
        query = 'select count(*) from aqxs_leaf_count_%s' % system_uid
        try:
            cursor.execute(query)
            leaf_count_count = cursor.fetchone()[0]
            if leaf_count_count > 0:
                print "problem in system: %s - no attached crops, but leaf count measurements" % system_uid
        except:
            # the table simply does not exist
            BROKEN_SYSTEMS.add(system_uid)

        query = 'select count(*) from aqxs_height_%s' % system_uid
        try:
            cursor.execute(query)
            height_count = cursor.fetchone()[0]
            if height_count > 0:
                print "problem in system: %s - no attached crops, but height measurements" % system_uid
        except:
            BROKEN_SYSTEMS.add(system_uid)

        return None
    else:
        return row[0]

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
    try:
        # 1. get system information and gather data integrity information
        cursor.execute('select id, system_uid from systems')
        systems = {pk: system_uid for pk, system_uid in cursor.fetchall()}
        crops = {}
        for pk, system_uid in systems.items():
            crop_id = get_default_crops(cursor, pk, system_uid)
            crops[pk] = crop_id

        # 2. alter the tables
        for pk, system_uid in systems.items():
            #cursor.execute('')
            print("updating tables for system %s..." % system_uid)
            if system_uid in BROKEN_SYSTEMS:
                print("broken data tables, skipping.")
            else:
                print("leaf_count...")
                table_name = 'aqxs_leaf_count_%s' % system_uid
                # drop the on update EXTRA
                try:
                    query = 'alter table %s add foreign_key integer not null' % table_name
                    #print(query)
                    cursor.execute(query)
                except:
                    # just in case we have done this already
                    pass
                crop_id = crops[pk]
                if not crop_id is None:
                    # here we need to process each entry individually.
                    # The reason ? Each measurement table somehow has an on_update
                    # trigger in its primary key column, which will be set to something
                    # wrong, so we need to make sure we remember that time stamp
                    print("set default crop id to: %d" % crop_id)
                    cursor.execute('select time from %s' % table_name)
                    for row in cursor.fetchall():
                        query = "update " + table_name + " set foreign_key=%s, time=%s where time=%s"
                        cursor2.execute(query, [crop_id, row[0], row[0]])

                print("height...")
                table_name = 'aqxs_height_%s' % system_uid
                try:
                    query = 'alter table %s add foreign_key integer not null' % table_name
                    #print(query)
                    cursor.execute(query)
                except:
                    # just in case we did this already
                    pass
                if not crop_id is None:
                    print("set default crop id to: %d" % crop_id)
                    cursor.execute('select time from %s' % table_name)
                    for row in cursor.fetchall():
                        query = "update " + table_name + " set foreign_key=%s, time=%s where time=%s"
                        cursor2.execute(query, [crop_id, row[0], row[0]])
        conn.commit()
    finally:
        cursor.close()
        conn.close()
    #print(crops)
    #print("BROKEN SYSTEMS: ", BROKEN_SYSTEMS)

