import uuid
import MySQLdb
import traceback


# TODO: This seems to be unnecessarily hard-coded
MEASUREMENTS = ['ammonium', 'o2', 'ph', 'nitrate', 'light', 'temp', 'nitrite', 'chlorine', 'hardness', 'alkalinity', 'leaf_count', 'height']

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

        systemID = 0

        query1 = (
        'INSERT INTO systems (user_id, name, system_uid, start_date, aqx_technique_id, location_lat, location_lng)'
        'VALUES (%s, %s, %s, %s, %s, %s, %s)')
        values1 = (userID, name, systemUID, startDate, techniqueID, locationLat, locationLng)
        query2 = 'INSERT INTO system_gb_media (system_id,gb_media_id) VALUES (%s, %s)'
        query3 = 'INSERT INTO system_aquatic_organisms VALUES (%s, %s, %s)'
        query4 = 'INSERT INTO system_crops VALUES (%s, %s, %s)'
        query5 = 'INSERT INTO system_status (system_uid, start_time, end_time) VALUES (%s, %s, "2030-12-31 23:59:59")'

        values5 = (systemUID, startDate)

        names = list(map(lambda x: 'aqxs_' + x + '_' + systemUID, MEASUREMENTS))
        # MySQL unfortunately has versions supporting different non-primary key timestamps
        # our production system (which runs on CentOS with ancient MySQL) does not accept
        # the default value, the newer development system requires a default value
        create_query1 = 'CREATE TABLE %s (time TIMESTAMP PRIMARY KEY NOT NULL, value DECIMAL(13,10) NOT NULL, updated_at TIMESTAMP)'
        create_query2 = 'CREATE TABLE %s (time TIMESTAMP PRIMARY KEY NOT NULL, value DECIMAL(13,10) NOT NULL, updated_at TIMESTAMP default current_timestamp)'

        try:
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
            for name in names:
                try:
                    cursor.execute(create_query1 % name)
                except:
                    cursor.execute(create_query2 % name)

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

    def update_system(self, system):
        conn = self.dbconn()
        cursor = conn.cursor()
        crops = system['crops']
        organisms = system['organisms']
        print(crops)
        print(organisms)
        try:
            cursor.execute('select id from systems where system_uid=%s', [system['UID']])
            system_id = cursor.fetchone()[0]
            cursor.execute('select organism_id,num from system_aquatic_organisms where system_id=%s',
                           [system_id])
            original_orgs = [(r[0], r[1]) for r in cursor.fetchall()]
            print("orig orgs: ", original_orgs)
            cursor.execute('select crop_id,num from system_crops where system_id=%s',
                           [system_id])
            original_crops = [(r[0], r[1]) for r in cursor.fetchall()]
            print("orig crops: ", original_crops)
            cursor.execute('update systems set name=%s where system_uid=%s', (system['name'], system['UID']))

            # determine whether need to change organisms or
            # plants
            update_organisms = True
            update_crops = True

            if update_organisms:
                cursor.execute('delete from system_aquatic_organisms where system_id=%s', [system_id])
                for o in organisms:
                    cursor.execute('insert into system_aquatic_organisms (system_id,organism_id,num) values (%s,%s,%s)', [system_id, o['ID'], o['count']])

            if update_crops:
                cursor.execute('delete from system_crops where system_id=%s', [system_id])
                for c in crops:
                    cursor.execute('insert into system_crops (system_id,crop_id,num) values (%s,%s,%s)', [system_id, c['ID'], c['count']])

            conn.commit()
        finally:
            cursor.close()
            conn.close()


def table_name(measurementType, systemUID):
    return 'aqxs_' + measurementType + '_' + systemUID
