# DAO for fetching all the data related to the measurements of the systems


class MeasurementsDAO:
    ###############################################################################
    # constructor to get connection
    def __init__(self, conn):
        self.conn = conn

    ###############################################################################
    # get_all_measurement_names: method to fetch the names of all the measurements
    def get_all_measurement_names(self):
        cursor = self.conn.cursor()
        query_names = ("SELECT name "
                       "FROM measurement_types;")
        try:
            cursor.execute(query_names)
            measurement_names = cursor.fetchall()
        finally:
            cursor.close()
        return measurement_names

    ###############################################################################
    # get_latest_value: get latest value from the given table
    def get_latest_value(self, table_name):
        cursor = self.conn.cursor()
        query = "SELECT * FROM %s " \
                "ORDER BY time DESC " \
                "LIMIT 1" % table_name
        try:
            cursor.execute(query)
            value = cursor.fetchall()
        finally:
            cursor.close()
        return value

    ###############################################################################
    def put_measurement_light(self, light, table_name):
        cursor = self.conn.cursor()
        query = ("INSERT INTO %s (time, value) "
                 "values(%s, %s)" % table_name)
        data = (light.get('time'), light.get('value'))
        try:
            cursor.execute(query, data)
            self.conn.commit()
        except:
            self.conn.rollback()
            cursor.close
            return "Insert error"
        finally:
            cursor.close
        return "Light measurement inserted"

    ###############################################################################

    # get_measurement_name: method to fetch the name of the measurements of the
    # given measurement_id
    def get_measurement_name(self, measurement_id):
        cursor = self.conn.cursor()
        query_name = ("SELECT name "
                      "FROM measurement_types "
                      "WHERE id = %s;")
        try:
            cursor.execute(query_name, (measurement_id, ))
            measurement_name, = cursor.fetchall()
        finally:
            cursor.close()
        return measurement_name

    ###############################################################################

    # Destructor to close the self connection
    def __del__(self):
        self.conn.close()
