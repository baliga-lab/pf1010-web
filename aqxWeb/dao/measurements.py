from aqxWeb.dao.systems import table_name as sys_table_name
import MySQLdb


class MeasurementDAO:
    def __init__(self, app):
        self.app = app

    def dbconn(self):
        return MySQLdb.connect(host=self.app.config['HOST'], user=self.app.config['USER'],
                               passwd=self.app.config['PASS'], db=self.app.config['DB'])

    def measurement_types(self):
        def to_float(s):
            return None if s is None else float(s)

        conn = self.dbconn()
        cursor = conn.cursor()
        cursor.execute('select id,name,unit,min,max,full_name from measurement_types where id < 9999')
        return [{'id': m_id, 'name': name, 'unit': unit, 'min': to_float(mmin), 'max': to_float(mmax), 'full_name': full_name}
                for m_id, name, unit, mmin, mmax, full_name in cursor.fetchall()]

    def latest_readings_for_system(self, systemUID):
        conn = self.dbconn()
        cursor = conn.cursor()
        readings = {}

        query = ('SELECT t.value, t.time, t.updated_at '
                 'FROM %s t '
                 'ORDER BY t.time DESC '
                 'LIMIT 1')

        try:
            measurement_types = self.measurement_types()
            readings = []
            for t in measurement_types:
                measurement = t['name']
                table = sys_table_name(measurement, systemUID)
                cursor.execute(query % table)
                reading = cursor.fetchone()
                new_reading = {'name': t['name'], 'full_name': t['full_name']}
                if reading:
                    new_reading['value'] = round(reading[0], 2) if reading[0] else None
                    new_reading['created_at'] = reading[1].strftime('%Y-%m-%d %H:%M:%S') if reading[1] else None
                    new_reading['updated_at'] = reading[2].strftime('%Y-%m-%d %H:%M:%S') if reading[2] else None
                readings.append(new_reading)
        finally:
            cursor.close()
            conn.close()

        return readings

    def submit_reading(self, measurementType, systemUID, reading):
        conn = self.dbconn()
        cursor = conn.cursor()

        value = reading['value']
        timestamp = reading['timestamp']
        table = sys_table_name(measurementType, systemUID)

        query = 'INSERT INTO ' + table + ' (value, time) VALUES (%s, %s)'

        try:
            cursor.execute(query, (value, timestamp))
            conn.commit()
        finally:
            cursor.close()
            conn.close()

        return cursor.lastrowid

    def store_measurements(self, system_uid, timestamp, measurements):
        """saves a list of measurements to the database"""
        if system_uid is not None and timestamp is not None and len(measurements) > 0:
            conn = self.dbconn()
            cursor = conn.cursor()
            try:
                for m in measurements:
                    table = sys_table_name(m[0], system_uid)
                    query = 'insert into ' + table + ' (value, time) values (%s, %s)'
                    cursor.execute(query, [m[1], timestamp])
                conn.commit()
            finally:
                cursor.close()
                conn.close()
