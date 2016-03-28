# DAO for fetching all the data related to the measurements of the systems
from mysql.connector import Error


class MeasurementsDAO:
    ###############################################################################
    # constructor to get connection
    def __init__(self, conn):
        self.conn = conn

    ###############################################################################
    # get_all_measurement_names: method to fetch the names of all the measurements
    # return: names of all the measurements
    def get_all_measurement_names(self):
        cursor = self.conn.cursor()
        query_names = ("SELECT name "
                       "FROM measurement_types;")
        try:
            cursor.execute(query_names)
            measurement_names = cursor.fetchall()
        except Error as e:
            return {'error': e.msg}
        finally:
            cursor.close()
        return measurement_names

    ###############################################################################
    # get_latest_value: get latest value from the given table
    # param - table_name: name of the table
    # param - num_of_records: number of last records to be retrieved
    # returns: last (num_of_records) from the given table_name
    def get_latest_value(self, table_name, num_of_records):
        cursor = self.conn.cursor()
        query_get = "SELECT * FROM %s " \
                    "ORDER BY time DESC " \
                    "LIMIT %%s" % table_name
        try:
            cursor.execute(query_get, (num_of_records, ))
            value = cursor.fetchall()
        except Error as e:
            return {'error': e.msg}
        finally:
            cursor.close()
        return value

    ###############################################################################
    # insert measurement value
    # param - table_name: name of the table
    # param - time : time to be inserted
    # param - value: value to be inserted corresponding to the given time
    # returns:
    #   (a) If successfully inserted: Record successfully inserted
    #   (b) If the value at the given time already exists: Value at the given time
    #       already recorded
    #   (c) If encountered an insertion error: error message
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
        except Error as e:
            self.conn.rollback()
            return {'error': e.msg}
        finally:
            cursor.close()
        return "Record successfully inserted"

    ###############################################################################
    # check if measurement exists
    # param - table_name: name of the table
    # param - time
    # returns:
    #   (a) If given time already present in the given table: Error
    #   (b) Else: returns the time
    def get_recorded_time(self, table_name, time):
        cursor = self.conn.cursor()
        query_time = "SELECT time " \
                     "FROM %s " \
                     "WHERE time = %%s" % table_name
        try:
            cursor.execute(query_time, (time, ))
            recorded_time = cursor.fetchall()
        except Error as e:
            return {'error': e.msg}
        finally:
            cursor.close()
        return recorded_time

    ###############################################################################
    # get_all_measurement_names: method to fetch the names of all the measurements
    # param - id_list: list of the measurement ids
    # returns: list of measurement names for the given ids.
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
            cursor.execute(query_names)
            measurement_names = cursor.fetchall()
        except Error as e:
            return {'error': e.msg}
        finally:
            cursor.close()

        return measurement_names

    ###############################################################################

    # get_measurement_name: method to fetch the name of the measurements of the
    # param - given measurement_id: id of a measurement
    # returns: name of the measurement for the given id
    def get_measurement_name(self, measurement_id):
        cursor = self.conn.cursor()
        query_name = ("SELECT name "
                      "FROM measurement_types "
                      "WHERE id = %s;")
        try:
            cursor.execute(query_name, (measurement_id, ))
            measurement_name, = cursor.fetchall()
        except Error as e:
            return {'error': e.msg}
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
        except Error as e:
            return {'error': e.msg + "system: :" + str(system) + "  measurements: " + str(measurements)}
        finally:
            cursor.close()

        # create new list for each measurement
        for s in systems:
            values[s] = {}
            for mea in measurements:
                values[s][mea] = []

        # add all measurements in a dict
        for s in systems:

            v = payload[s]

            if v:
                for m in v:
                    key = m[0]
                    values[s][key].append(m)

            payload[s] = values[s]

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

    # get_all_measurement_info: method to fetch the id, name, units, min and max
    #                           of all the measurements
    # returns the id, name, units, min, max of all the measurements
    def get_all_measurement_info(self):
        cursor = self.conn.cursor()
        query_mea_info = ("SELECT * "
                          "FROM measurement_types;")
        try:
            cursor.execute(query_mea_info)
            measurement_info = cursor.fetchall()
        except Error as e:
            return {'error': e.msg}
        finally:
            cursor.close()
        return measurement_info

    # Destructor to close the self connection
    def __del__(self):
        self.conn.close()
