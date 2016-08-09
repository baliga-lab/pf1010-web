import MySQLdb

class metadataDAO:
    def __init__(self, app):
        self.app = app

    def getDBConn(self):
        return MySQLdb.connect(host=self.app.config['HOST'], user=self.app.config['USER'],
                               passwd=self.app.config['PASS'], db=self.app.config['DB'])

    def getEnums(self):
        conn = self.getDBConn()
        cursor = conn.cursor()

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
            conn.close()
        return results