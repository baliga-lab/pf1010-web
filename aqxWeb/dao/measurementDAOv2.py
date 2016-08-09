from systemDAOv2 import getTableName
import MySQLdb

class measurementDAO:
    def __init__(self, app):
        self.app = app

    def getDBConn(self):
        return MySQLdb.connect(host=self.app.config['HOST'], user=self.app.config['USER'],
                               passwd=self.app.config['PASS'], db=self.app.config['DB'])

    def getLatestReadingsForSystem(self, systemUID):
        conn = self.getDBConn()
        cursor = conn.cursor()

        measurements = ['ammonium', 'o2', 'ph', 'nitrate', 'light', 'temp', 'nitrite', 'chlorine', 'hardness', 'alkalinity']

        readings = {}

        query = ('SELECT t.value '
                 'FROM %s t '
                 'ORDER BY t.time DESC '
                 'LIMIT 1')

        try:
            readings = []
            for measurement in measurements:
                table = getTableName(measurement, systemUID)
                cursor.execute(query % table)
                reading = cursor.fetchone()
                if reading:
                    reading = round(reading[0], 2)
                readings.append({
                    'name': measurement,
                    'value': reading
                })
        except:
            raise
        finally:
            cursor.close()
            conn.close()

        return readings

    def submitReading(self, measurementType, systemUID, reading):
        conn = self.getDBConn()
        cursor = conn.cursor()

        value = reading['value']
        timestamp = reading['timestamp']

        table = getTableName(measurementType, systemUID)

        query = ('INSERT INTO ' + table + ' (value, time) '
                 'VALUES (%s, %s)')

        values = (value, timestamp)

        try:
            cursor.execute(query, values)
            conn.commit()
        except:
            conn.rollback()
            raise
        finally:
            cursor.close()
            conn.close()

        return cursor.lastrowid



