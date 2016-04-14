from systemDAOv2 import getTableName


class measurementDAO:

    def __init__(self, conn):
        self.conn = conn


    def getLatestReadingsForSystem(self, systemUID):
        cursor = self.conn.cursor()

        measurements = ['ammonium', 'o2', 'ph', 'nitrate', 'light', 'temp', 'nitrite', 'chlorine', 'hardness', 'alkalinity']

        readings = {}

        query = ('SELECT t.value '
                 'FROM %s t '
                 'ORDER BY t.time DESC '
                 'LIMIT 1')

        try:
            for measurement in measurements:
                table = getTableName(measurement, systemUID)
                cursor.execute(query % table)
                reading = cursor.fetchone()
                readings[measurement] = reading
        except:
            raise
        finally:
            cursor.close()

        return readings


    def submitReading(self, measurementType, systemUID, reading):
        cursor = self.conn.cursor()

        value = reading['value']
        timestamp = reading['timestamp']

        table = getTableName(measurementType, systemUID)

        query = ('INSERT INTO ' + table + ' (value, time) '
                 'VALUES (%s, %s)')

        values = (value, timestamp)

        try:
            cursor.execute(query, values)
            self.conn.commit()
        except:
            self.conn.rollback()
            raise
        finally:
            cursor.close()

        return cursor.lastrowid


