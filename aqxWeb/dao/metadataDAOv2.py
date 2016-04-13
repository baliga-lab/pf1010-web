class metadataDAO:

    def __init__(self, conn):
        self.conn = conn

    def getEnums(self):
        cursor = self.conn.cursor()

        query = ("SELECT \'crops\', c.id, c.name FROM crops c UNION "
                 "SELECT \'techniques\' , t.id, t.name  FROM aqx_techniques t UNION "
                 "SELECT \'organisms\', ao.id, ao.name FROM aquatic_organisms ao UNION "
                 "SELECT \'growbedMedia\', gm.id, gm.name FROM growbed_media gm UNION "
                 "SELECT \'statuses\', st.id, st.status_type FROM status_types st")

        try:
            cursor.execute(query)
            results = cursor.fetchall()
        except:
            raise
        finally:
            cursor.close()

        return results