import uuid
import MySQLdb

class systemDAO:
    def __init__(self, app):
        self.app = app

    def getDBConn(self):
        return MySQLdb.connect(host=self.app.config['HOST'], user=self.app.config['USER'],
                               passwd=self.app.config['PASS'], db=self.app.config['DB'])

    def getSystem(self, system_uid):
        conn = self.getDBConn()
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
        except:
            raise
        finally:
            cursor.close()
            conn.close()

        return result

    def getStatusForSystem(self, system_uid):
        conn = self.getDBConn()
        cursor = conn.cursor()

        query = ("SELECT st.status_type "
                 "FROM system_status ss "
                 "LEFT JOIN status_types st ON ss.sys_status_id = st.id "
                 "WHERE ss.system_uid = %s "
                 "ORDER BY ss.id DESC "
                 "LIMIT 1")

        try:
            cursor.execute(query, (system_uid,))
            result = cursor.fetchone()
        except:
            raise
        finally:
            cursor.close()
            conn.close()

        return result

    def getOrganismsForSystem(self, system_id):
        conn = self.getDBConn()
        cursor = conn.cursor()

        query = ("SELECT ao.name, sao.num as 'count' "
                 "FROM system_aquatic_organisms sao "
                 "LEFT JOIN aquatic_organisms ao ON sao.organism_id = ao.id "
                 "WHERE sao.system_id = %s")

        try:
            cursor.execute(query, (system_id,))
            results = cursor.fetchall()
        except:
            raise
        finally:
            cursor.close()
            conn.close()

        return results

    def getCropsForSystem(self, system_id):
        conn = self.getDBConn()
        cursor = conn.cursor()

        query = ("SELECT c.name, sc.num as 'count' "
                 "FROM system_crops sc "
                 "LEFT JOIN crops c ON sc.crop_id = c.id "
                 "WHERE sc.system_id = %s")

        try:
            cursor.execute(query, (system_id,))
            results = cursor.fetchall()
        except:
            raise
        finally:
            cursor.close()
            conn.close()

        return results

    def getGrowBedMediaForSystem(self, system_id):
        conn = self.getDBConn()
        cursor = conn.cursor()

        query = ("SELECT gm.name, sgm.num as 'count' "
                 "FROM system_gb_media sgm "
                 "LEFT JOIN growbed_media gm ON sgm.gb_media_id = gm.id "
                 "WHERE sgm.system_id = %s")

        try:
            cursor.execute(query, (system_id,))
            results = cursor.fetchall()
        except:
            raise
        finally:
            cursor.close()
            conn.close()

        return results

    def createSystem(self, system):
        conn = self.getDBConn()
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

        # The following inserts into systems table

        query1 = (
        'INSERT INTO systems (user_id, name, system_uid, start_date, aqx_technique_id, location_lat, location_lng)'
        'VALUES (%s, %s, %s, %s, %s, %s, %s)')

        values1 = (userID, name, systemUID, startDate, techniqueID, locationLat, locationLng)

        # The following insert into system_gb_media table, system_aquatic_organisms, and system_crops

        query2 = ('INSERT INTO system_gb_media '
                  'VALUES (%s, %s, %s)')

        query3 = ('INSERT INTO system_aquatic_organisms '
                  'VALUES (%s, %s, %s)')

        query4 = ('INSERT INTO system_crops '
                  'VALUES (%s, %s, %s)')

        query5 = ('INSERT INTO system_status (system_uid, start_time, end_time) '
                  'VALUES (%s, %s, "2030-12-31 23:59:59")')

        values5 = (systemUID, startDate)

        # The following create measurement tables

        measurements = ['ammonium', 'o2', 'ph', 'nitrate', 'light', 'temp', 'nitrite', 'chlorine', 'hardness', 'alkalinity']
        names = list(map(lambda x: 'aqxs_' + x + '_' + systemUID, measurements))
        query6 = 'CREATE TABLE %s (time TIMESTAMP PRIMARY KEY NOT NULL, value DECIMAL(13,10) NOT NULL)'

        # Execute the queries

        try:
            cursor.execute(query1, values1)
            systemID = cursor.lastrowid
            for medium in gbMedia:
                values2 = (systemID, medium['ID'], medium['count'])
                cursor.execute(query2, values2)
            for organism in organisms:
                values3 = (systemID, organism['ID'], organism['count'])
                cursor.execute(query3, values3)
            for crop in crops:
                values4 = (systemID, crop['ID'], crop['count'])
                cursor.execute(query4, values4)
            cursor.execute(query5, values5)
            for name in names:
                cursor.execute(query6 % name)
            conn.commit()
        except:
            conn.rollback()
            raise
        finally:
            cursor.close()
            conn.close()

        return {'userID': userID, 'systemID': systemID, 'systemUID': systemUID}

    def getSystemsForUser(self, userID):
        conn = self.getDBConn()
        cursor = conn.cursor()

        query = ('SELECT s.id, s.system_uid, s.name '
                 'FROM systems s '
                 'WHERE s.user_id = %s')

        try:
            cursor.execute(query, (userID,))
            results = cursor.fetchall()
        except:
            raise
        finally:
            cursor.close()
            conn.close()

        return results


    def getSystemID(self, systemUID):
        conn = self.getDBConn()
        cursor = conn.cursor()

        query = ('SELECT s.id '
                 'FROM systems s '
                 'WHERE s.system_uid = %s')

        try:
            cursor.execute(query, (systemUID,))
            result = cursor.fetchone()
        except:
            raise
        finally:
            cursor.close()
            conn.close()

        return result


    def deleteSystem(self, systemUID):
        conn = self.getDBConn()
        cursor = conn.cursor()

        systemID = self.getSystemID(systemUID)

        # The following deletes from system table

        query1 = ('DELETE FROM systems s '
                  'WHERE s.system_uid = %s '
                  'LIMIT 1;')

        # The following delete from system_gb_media table, system_aquatic_organisms, and system_crops

        query2 = ('DELETE FROM system_gb_media sgm '
                  'WHERE sgm.system_id = %s;')

        query3 = ('DELETE FROM system_aquatic_organisms sao '
                  'WHERE sao.system_id = %s;')

        query4 = ('DELETE FROM system_crops_media sc '
                  'WHERE sc.system_id = %s;')

        # The following will delete measurement tables

        measurements = ['ammonium', 'o2', 'ph', 'nitrate', 'light', 'temp', 'nitrite', 'chlorine', 'hardness', 'alkalinity']
        names = list(map(lambda x: 'aqxs_' + x + '_' + systemUID, measurements))
        query5 = 'DROP TABLE IF EXISTS %s'

        try:
            cursor.execute(query1, (systemUID,))
            cursor.execute(query2, (systemID,))
            cursor.execute(query3, (systemID,))
            cursor.execute(query4, (systemID,))
            for name in names:
                cursor.execute(query5 % name)
            conn.commit()
        except:
            conn.rollback()
            raise
        finally:
            cursor.close()
            conn.close()

        return True


def getTableName(measurementType, systemUID):
    return 'aqxs_' + measurementType + '_' + systemUID
