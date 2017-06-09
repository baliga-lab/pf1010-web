from aqxWeb.utils import get_measurement_table_name
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
        cursor.execute('select id,name,unit,min,max,full_name from measurement_types where id < 9999 order by order_num')
        return [{'id': m_id, 'name': name, 'unit': unit, 'min': to_float(mmin), 'max': to_float(mmax), 'full_name': full_name}
                for m_id, name, unit, mmin, mmax, full_name in cursor.fetchall()]

        return readings

    def latest_measurements(self, system_uid):
        mtypes = self.measurement_types()
        conn = self.dbconn()
        cursor = conn.cursor()
        result = {}
        for mt in mtypes:
            table = get_measurement_table_name(mt['name'], system_uid)
            cursor.execute('select time,value from %s order by time desc limit 1' % table)
            row = cursor.fetchone()
            if row is not None:
                time, value = row
                value = float(value)
            else:
                time, value = None, None
            result[mt['name']] = value
        return result

    def store_measurements(self, system_uid, timestamp, measurements):
        """saves a list of measurements to the database"""
        if system_uid is not None and timestamp is not None and len(measurements) > 0:
            conn = self.dbconn()
            cursor = conn.cursor()
            try:
                for m in measurements:
                    table = get_measurement_table_name(m[0], system_uid)
                    query = 'insert into ' + table + ' (value, time) values (%s, %s)'
                    cursor.execute(query, [m[1], timestamp])
                conn.commit()
            finally:
                cursor.close()
                conn.close()

    def update_measurement(self, system_uid, timestamp, measurement, value):
        conn = self.dbconn()
        cursor = conn.cursor()
        try:
            table = get_measurement_table_name(measurement, system_uid)
            query = 'update ' + table + ' set value=%s,time=%s,updated_at=CURRENT_TIMESTAMP where time=%s'
            cursor.execute(query, [value, timestamp, timestamp])
            conn.commit()
        finally:
            cursor.close()
            conn.close()

    def delete_measurement(self, system_uid, timestamp, measurement):
        conn = self.dbconn()
        cursor = conn.cursor()
        try:
            table = get_measurement_table_name(measurement, system_uid)
            query = 'delete from ' + table + ' where time=%s'
            cursor.execute(query, [timestamp])
            conn.commit()
        finally:
            cursor.close()
            conn.close()
