import uuid
import MySQLdb
import traceback
from aqxWeb.utils import get_measurement_table_name


class SystemDAO:
    def __init__(self, app):
        self.app = app

    def dbconn(self):
        return MySQLdb.connect(host=self.app.config['HOST'], user=self.app.config['USER'],
                               passwd=self.app.config['PASS'], db=self.app.config['DB'])

    def get_system(self, system_uid):
        conn = self.dbconn()
        cursor = conn.cursor()

        query = (
        "SELECT s.id, s.system_uid, s.user_id, s.name, s.creation_time, s.start_date, s.location_lat, s.location_lng, "
        "aqt.name as 'aqx_technique', "
        "st.status_type as 'status' "
        "FROM systems s "
        "LEFT JOIN aqx_techniques aqt ON s.aqx_technique_id = aqt.id "
        "LEFT JOIN status_types st    ON s.status = st.id "
        "WHERE s.system_uid = %s")

        try:
            cursor.execute(query, (system_uid,))
            result = cursor.fetchone()
        finally:
            cursor.close()
            conn.close()

        return result

    def getStatusForSystem(self, system_uid):
        conn = self.dbconn()
        cursor = conn.cursor()

        query = ("SELECT st.status_type FROM system_status ss "
                 "LEFT JOIN status_types st ON ss.sys_status_id = st.id "
                 "WHERE ss.system_uid = %s "
                 "ORDER BY ss.id DESC "
                 "LIMIT 1")

        try:
            cursor.execute(query, (system_uid,))
            result = cursor.fetchone()
        finally:
            cursor.close()
            conn.close()

        return result

    def organisms_for_system(self, system_id):
        conn = self.dbconn()
        cursor = conn.cursor()

        query = ("SELECT ao.id,ao.name,sao.num as 'count' "
                 "FROM system_aquatic_organisms sao "
                 "LEFT JOIN aquatic_organisms ao ON sao.organism_id = ao.id "
                 "WHERE sao.system_id = %s")

        try:
            cursor.execute(query, (system_id,))
            results = cursor.fetchall()
        finally:
            cursor.close()
            conn.close()

        return results

    def crops_for_system(self, system_id):
        conn = self.dbconn()
        cursor = conn.cursor()

        query = ("SELECT c.id,c.name,sc.num as 'count' "
                 "FROM system_crops sc "
                 "LEFT JOIN crops c ON sc.crop_id = c.id "
                 "WHERE sc.system_id = %s")

        try:
            cursor.execute(query, (system_id,))
            results = cursor.fetchall()
        finally:
            cursor.close()
            conn.close()

        return results

    def getGrowBedMediaForSystem(self, system_id):
        conn = self.dbconn()
        cursor = conn.cursor()

        query = ("SELECT gm.name, sgm.num as 'count' "
                 "FROM system_gb_media sgm "
                 "LEFT JOIN growbed_media gm ON sgm.gb_media_id = gm.id "
                 "WHERE sgm.system_id = %s")

        try:
            cursor.execute(query, (system_id,))
            results = cursor.fetchall()
        finally:
            cursor.close()
            conn.close()

        return results

    def create_system(self, system):
        conn = self.dbconn()
        cursor = conn.cursor()

        userID = system['userID']
        name = system['name']
        systemUID = str(uuid.uuid1().hex)
        startDate = system['startDate']
        techniqueID = system['techniqueID']
        location = system['location']
        locationLat = location['lat']
        locationLng = location['lng']
        gbMedia = system['gbMedia']
        crops = system['crops']
        organisms = system['organisms']
        status = system['status']
        systemID = 0

        query1 = (
            'INSERT INTO systems (user_id, name, system_uid, start_date, aqx_technique_id, location_lat, location_lng, status)'
            'VALUES (%s, %s, %s, %s, %s, %s, %s, %s)')
        values1 = (userID, name, systemUID, startDate, techniqueID, locationLat, locationLng, status)
        query2 = 'INSERT INTO system_gb_media (system_id,gb_media_id) VALUES (%s, %s)'
        query3 = 'INSERT INTO system_aquatic_organisms VALUES (%s, %s, %s)'
        query4 = 'INSERT INTO system_crops VALUES (%s, %s, %s)'
        # note: database table column sys_status_id  is set to 100 on default
        query5 = 'INSERT INTO system_status (system_uid, start_time, end_time) VALUES (%s, %s, "2030-12-31 23:59:59")'

        values5 = (systemUID, startDate)

        # MySQL unfortunately has versions supporting different non-primary key timestamps
        # our production system (which runs on CentOS with ancient MySQL) does not accept
        # the default value, the newer development system requires a default value
        create_single_query1 = 'CREATE TABLE %s (time TIMESTAMP PRIMARY KEY NOT NULL, value DECIMAL(13,10) NOT NULL, updated_at TIMESTAMP)'
        create_single_query2 = 'CREATE TABLE %s (time TIMESTAMP PRIMARY KEY NOT NULL, value DECIMAL(13,10) NOT NULL, updated_at TIMESTAMP default current_timestamp)'

        # create multi table if the measurement type is marked as such
        create_multi_query1 = 'CREATE TABLE %s (time TIMESTAMP PRIMARY KEY NOT NULL, value DECIMAL(13,10) NOT NULL, updated_at TIMESTAMP, foreign_key integer not null)'
        create_multi_query2 = 'CREATE TABLE %s (time TIMESTAMP PRIMARY KEY NOT NULL, value DECIMAL(13,10) NOT NULL, updated_at TIMESTAMP default current_timestamp, foreign_key integer not null)'

        try:
            cursor.execute('select name, multi_table from measurement_types where id < 100000')
            meas_types = {name: multi_table for name, multi_table in cursor.fetchall()}

            cursor.execute(query1, values1)
            systemID = cursor.lastrowid
            for medium in gbMedia:
                cursor.execute(query2, (systemID, medium['ID']))
            for organism in organisms:
                if organism['ID'] > 0:
                    cursor.execute(query3, (systemID, organism['ID'], organism['count']))
            for crop in crops:
                if crop['ID'] > 0:
                    cursor.execute(query4, (systemID, crop['ID'], crop['count']))
            cursor.execute(query5, values5)

            # make sure the query is creating the table in either production system
            # or dev system format
            for name, multi_table in meas_types.items():
                table_name = get_measurement_table_name(name, systemUID)
                try:
                    if multi_table is None:
                        cursor.execute(create_single_query1 % table_name)
                    else:
                        cursor.execute(create_multi_query1 % table_name)
                except:
                    if multi_table is None:
                        cursor.execute(create_single_query2 % table_name)
                    else:
                        cursor.execute(create_multi_query2 % table_name)

            conn.commit()
        finally:
            cursor.close()
            conn.close()

        return {'userID': userID, 'systemID': systemID, 'systemUID': systemUID}

    def getSystemsForUser(self, userID):
        conn = self.dbconn()
        cursor = conn.cursor()

        query = 'SELECT s.id, s.system_uid, s.name FROM systems s WHERE s.user_id = %s'

        try:
            cursor.execute(query, (userID,))
            results = cursor.fetchall()
        finally:
            cursor.close()
            conn.close()

        return results


    def getSystemID(self, systemUID):
        conn = self.dbconn()
        cursor = conn.cursor()

        query = 'SELECT s.id FROM systems s WHERE s.system_uid = %s'

        try:
            cursor.execute(query, (systemUID,))
            result = cursor.fetchone()
        finally:
            cursor.close()
            conn.close()

        return result

    def delete_crop_from_system(self, system_uid, crop_id):
        conn = self.dbconn()
        cursor = conn.cursor()
        try:
            cursor.execute('select id from systems where system_uid=%s', [system_uid])
            system_pk = cursor.fetchone()[0]
            cursor.execute('delete from system_crops where system_id=%s and crop_id=%s',
                           [system_pk, crop_id])
            conn.commit()
        finally:
            cursor.close()
            conn.close()

    def delete_organism_from_system(self, system_uid, organism_id):
        conn = self.dbconn()
        cursor = conn.cursor()
        try:
            cursor.execute('select id from systems where system_uid=%s', [system_uid])
            system_pk = cursor.fetchone()[0]
            cursor.execute('delete from system_aquatic_organisms where system_id=%s and organism_id=%s',
                           [system_pk, organism_id])
            conn.commit()
        finally:
            cursor.close()
            conn.close()

    def update_system(self, system):
        conn = self.dbconn()
        cursor = conn.cursor()
        crops = system['crops']
        organisms = system['organisms']
        try:
            cursor.execute('select id from systems where system_uid=%s', [system['UID']])
            system_id = cursor.fetchone()[0]
            cursor.execute('select organism_id,num from system_aquatic_organisms where system_id=%s',
                           [system_id])
            original_orgs = [(r[0], r[1]) for r in cursor.fetchall()]
            cursor.execute('select crop_id,num from system_crops where system_id=%s',
                           [system_id])
            original_crops = [(r[0], r[1]) for r in cursor.fetchall()]
            cursor.execute('update systems set name=%s where system_uid=%s', (system['name'], system['UID']))

            # determine whether need to change organisms or
            # plants
            update_organisms = True
            update_crops = True

            if update_organisms:
                # Never delete the relationship in UPDATE !!!
                for o in organisms:
                    cursor.execute('select count(*) from system_aquatic_organisms where system_id=%s and organism_id=%s', [system_id, o['ID']])
                    if cursor.fetchone()[0] == 0:
                        if o['ID'] > 0:
                            cursor.execute('insert into system_aquatic_organisms (system_id,organism_id,num) values (%s,%s,%s)',
                                           [system_id, o['ID'], o['count']])
                    else:
                        cursor.execute('update system_aquatic_organisms set num=%s where system_id=%s and organism_id=%s', [o['count'], system_id, o['ID']])

            if update_crops:
                # Never delete the relationship in UPDATE !!!
                for c in crops:
                    cursor.execute('select count(*) from system_crops where system_id=%s and crop_id=%s',
                                   [system_id, c['ID']])
                    if cursor.fetchone()[0] == 0:
                        if c['ID'] > 0:
                            cursor.execute('insert into system_crops (system_id,crop_id,num) values (%s,%s,%s)',
                                           [system_id, c['ID'], c['count']])
                    else:
                        cursor.execute('update system_crops set num=%s where system_id=%s and crop_id=%s',
                                       [c['count'], system_id, c['ID']])

            conn.commit()
        finally:
            cursor.close()
            conn.close()
