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

    # get_measurements: method to fetch measurements for multiple systems
    # param system list of system_id
    # param measurements list of measurements
    # return dictionary with system_id as key and list of measurements[timestamp,m1,m2,...]
    # with key as the measurement
    def get_measurements(self, systems, measurements):
        payload = {}
        values = {}
        cursor = self.conn.cursor()
        try:
            for system in systems:
                query = self.create_query1(system,measurements)
                cursor.execute(query)
                payload[system] = cursor.fetchall()
        finally:
            cursor.close()

        #create new list for each measurement
        for mea in measurements:
            values[mea] = []

        #add all measurements in a dict
        for s in systems:
            v = payload[s]
            for m in v:
                values[m[0]].append(m)
            payload[s] = values
        return payload

    ###############################################################################

    # create_query2: method to create query to fetch measurements from a system with matching time
    # param system system_id
    # param measurements list of measurements
    # return query
    def create_query2(self, system, measurements):
        fields = "select " + measurements[0] + ".time," + measurements[0] + ".value as " + measurements[0] + ","
        tables = " from aqxs_" + measurements[0] + "_" + system + " " + measurements[0] + ","
        where = " where HOUR(" + measurements[0] + ".time) ="
        for i in range(1, len(measurements)):
            if i == len(measurements)-1:
                fields += measurements[i] + ".value as " + measurements[i]
                tables += "aqxs_" + measurements[i] + "_" + system + " " + measurements[i]
                where += " HOUR(" + measurements[i] + ".time) "
            else:
                fields += measurements[i] + ".value as " + measurements[i] + ","
                tables += "aqxs_" + measurements[i] + "_" + system + " " + measurements[i] + ","
                where += " HOUR(" + measurements[i] + ".time) and HOUR(" + measurements[i] + ".time) = "

        q = fields + tables + where + "group by " + measurements[0] + ".time " + "order by " + measurements[0] + ".time"
        return q


    ###############################################################################

    # create_query1: method to create query to fetch measurements from a system
    # param system system_id
    # param measurements list of measurements
    # return query
    def create_query1(self, system, measurements):
        query= ""
        for i in range(0, len(measurements)):
            if i == len(measurements)-1:
                query += "select \'"+ measurements[i] + "\'," + measurements[i] + ".time as time," \
                 + measurements[i] + ".value as value from aqxs_" + measurements[i] + "_" + system \
                     + " " + measurements[i]
            else:
                query += "select \'"+ measurements[i] + "\'," + measurements[i] + ".time as time," \
                 + measurements[i] + ".value as value from aqxs_" + measurements[i] + "_" + system \
                     + " " + measurements[i] + " union "
        return query

    ###############################################################################

    # Destructor to close the self connection
    def __del__(self):
        self.conn.close()


if __name__ == "__main__":
    m = MeasurementsDAO("")
    ml = ["o2","ph","light"];
    query = m.create_query1("555d0cfe9ebc11e58153000c29b92d09",ml)
    print query