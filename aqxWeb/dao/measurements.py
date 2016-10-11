from aqxWeb.dao.systems import table_name as sys_table_name
import MySQLdb

class MeasurementDAO:
    def __init__(self, app):
        self.app = app

    def getDBConn(self):
        return MySQLdb.connect(host=self.app.config['HOST'], user=self.app.config['USER'],
                               passwd=self.app.config['PASS'], db=self.app.config['DB'])

    def getLatestReadingsForSystem(self, systemUID):
        conn = self.getDBConn()
        cursor = conn.cursor()

        measurements = ['ammonium', 'o2', 'ph', 'nitrate', 'light', 'temp', 'nitrite', 'chlorine', 'hardness', 'alkalinity', 'leaf_count', 'height']

        readings = {}

        query = ('SELECT t.value, t.time, t.updated_at '
                 'FROM %s t '
                 'ORDER BY t.time DESC '
                 'LIMIT 1')

        try:
            readings = []
            for measurement in measurements:
                table = sys_table_name(measurement, systemUID)
                cursor.execute(query % table)
                reading = cursor.fetchone()
                new_reading = {'name': measurement}
                if reading:
                    # reading = round(reading[0], 2)
                    new_reading['value'] = round(reading[0], 2) if reading[0] else None
                    new_reading['created_at'] = reading[1].strftime('%Y-%m-%d %H:%M:%S') if reading[1] else None
                    new_reading['updated_at'] = reading[2].strftime('%m/%d/%y') if reading[2] else None
                    # readings.append({
                    #     'name': measurement,
                    #     'value': round(reading[0],2) if reading[0] else None,
                    #     'created_at': reading[1].strftime('%Y-%m-%d %H:%M:%S'),
                    #     'updated_at': reading[2].strftime('%Y-%m-%d %H:%M:%S')
                    # })
                readings.append(new_reading)
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

        table = sys_table_name(measurementType, systemUID)

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



