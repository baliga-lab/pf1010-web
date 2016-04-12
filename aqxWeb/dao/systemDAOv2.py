import uuid


class systemDAO:
    def __init__(self, conn):
        self.conn = conn

    def getSystem(self, system_uid):
        cursor = self.conn.cursor()

        query = ("SELECT s.id, s.system_uid, s.user_id, s.name, s.creation_time, s.start_date, s.location_lat, s.location_lng, "
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

        return result


    def getOrganismsForSystem(self, system_id):
        cursor = self.conn.cursor()

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

        return results


    def getCropsForSystem(self, system_id):
        cursor = self.conn.cursor()

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

        return results


    def getGrowBedMediaForSystem(self, system_id):
        cursor = self.conn.cursor()

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

        return results


    def createSystem(self, system):
        cursor = self.conn.cursor()

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

        query1 = ('INSERT INTO systems (user_id, name, system_uid, start_date, aqx_technique_id, location_lat, location_lng)'
                  'VALUES (%s, %s, %s, %s, %s, %s, %s)')

        values1 = (userID, name, systemUID, startDate, techniqueID, locationLat, locationLng)

        # The following insert into system_gb_media table, system_aquatic_organisms, and, system_crops

        query2 = ('INSERT INTO system_gb_media VALUES (%s, %s, %s)')

        query3 = ('INSERT INTO system_aquatic_organisms VALUES (%s, %s, %s)')

        query4 = ('INSERT INTO system_crops VALUES (%s, %s, %s)')

        # Execute the queries

        try:
            cursor.execute(query1, values1)
            self.conn.commit()
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
            self.conn.commit()
        except:
            self.conn.rollback()
            raise
        finally:
            cursor.close()

        return {'userID': userID, 'systemID': systemID, 'systemUID': systemUID}


    def getSystemsForUser(self, userID):
        cursor = self.conn.cursor()

        query = ('SELECT s.id, s.system_uid, s.name '
                 'FROM systems s '
                 'WHERE s.user_id = %s')

        try:
            cursor.execute(query, (userID,))
            result = cursor.fetchall()
        except:
            raise
        finally:
            cursor.close()

        return result
