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
    def get_latest_value(self, table_name, num_of_records):
        cursor = self.conn.cursor()
        query_get = "SELECT * FROM %s " \
                    "ORDER BY time DESC " \
                    "LIMIT %%s" % table_name
        try:
            cursor.execute(query_get, (num_of_records, ))
            value = cursor.fetchall()
        finally:
            cursor.close()
        return value

    ###############################################################################
    def put_system_measurement(self, table_name, time, value):
        time_already_recorded = self.get_recorded_time(table_name, time)
        if len(time_already_recorded) != 0:
            return "Value at the given time already recorded"
        cursor = self.conn.cursor()
        query_put = "INSERT INTO %s " \
                    "(time, value) " \
                    "VALUES (%%s, %%s)" % table_name
        record = (time, value)
        try:
            cursor.execute(query_put, record)
            self.conn.commit()
        except:
            self.conn.rollback()
            cursor.close()
            return "Insert error"
        finally:
            cursor.close()
        return "Record successfully inserted"

    ###############################################################################

    def get_recorded_time(self, table_name, time):
        cursor = self.conn.cursor()
        query_time = "SELECT time " \
                     "FROM %s " \
                     "WHERE time = %%s" % table_name
        try:
            cursor.execute(query_time, (time, ))
            recorded_time = cursor.fetchall()
        finally:
            cursor.close()
        return recorded_time

    ###############################################################################
    # get_all_measurement_names: method to fetch the names of all the measurements
    def get_measurement_name_list(self,id_list):
        cursor = self.conn.cursor()

        id_list_str = "("
        for i in range(0, len(id_list)):
            id_list_str = id_list_str + str(id_list[i]) + ","

        id_list_str = list(id_list_str)
        id_list_str[len(id_list_str) - 1] = ")"

        id_list_str = ''.join(id_list_str)


        query_names = ("SELECT name "
                       "FROM measurement_types "
                       "where id in " +
                       id_list_str)

        try:
            cursor.execute(query_names,id_list_str)
            measurement_names = cursor.fetchall()
        finally:
            cursor.close()

        return measurement_names

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
                print query
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
            print s
            if v:
                for m in v:
                    values[m[0]].append(m)
            else:
                 values = {}

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
                     + " " + measurements[i] + " order by time "
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