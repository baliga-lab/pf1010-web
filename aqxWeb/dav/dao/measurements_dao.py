# DAO for fetching all the data related to the measurements of the systems
import MySQLdb

class MeasurementsDAO:


    def __init__(self, app):
        self.app = app

    def getDBConn(self):
        return MySQLdb.connect(host=self.app.config['HOST'], user=self.app.config['USER'],
                               passwd=self.app.config['PASS'], db=self.app.config['DB'])
    ###############################################################################
    # get_all_measurement_names: method to fetch the names of all the measurements
    # return: names of all the measurements
    def get_all_measurement_names(self):
        conn = self.getDBConn()
        cursor = conn.cursor()
        query_names = ("SELECT name "
                       "FROM measurement_types;")
        try:
            cursor.execute(query_names)
            measurement_names = cursor.fetchall()
        except Exception as e:
            return {'error': e.args[1]}
        finally:
            cursor.close()
            conn.close()
        return measurement_names

    ###############################################################################
    # get_latest_value: get latest value from the given table
    # param - table_name: name of the table
    # param - num_of_records: number of last records to be retrieved
    # returns: last (num_of_records) from the given table_name
    def get_latest_value(self, table_name, num_of_records):
        conn = self.getDBConn()
        cursor = conn.cursor()
        query_get = "SELECT * FROM %s " \
                    "ORDER BY time DESC " \
                    "LIMIT %%s" % table_name
        try:
            cursor.execute(query_get, (num_of_records,))
            value = cursor.fetchall()
        except Exception as e:
            return {'error': e.args[1]}
        finally:
            cursor.close()
            conn.close()
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
        conn = self.getDBConn()
        time_already_recorded = self.get_recorded_time(table_name, time)
        if len(time_already_recorded) != 0:
            return {'error': 'Value at the given time already recorded'}
        cursor = conn.cursor()
        query_put = "INSERT INTO %s " \
                    "(time, value) " \
                    "VALUES (%%s, %%s)" % table_name
        record = (time, value)
        try:
            cursor.execute(query_put, record)
            conn.commit()
        except Exception as e:
            conn.rollback()
            return {'error': e.args[1]}
        finally:
            cursor.close()
            conn.close()
        return "Record successfully inserted"

    ###############################################################################
    # check if measurement exists
    # param - table_name: name of the table
    # param - time
    # returns:
    #   (a) If given time already present in the given table: Error
    #   (b) Else: returns the time
    def get_recorded_time(self, table_name, time):
        conn = self.getDBConn()
        cursor = conn.cursor()
        query_time = "SELECT time " \
                     "FROM %s " \
                     "WHERE time = %%s" % table_name
        try:
            cursor.execute(query_time, (time,))
            recorded_time = cursor.fetchall()
        except Exception as e:
            return {'error': e.args[1]}
        finally:
            cursor.close()
            conn.close()
        return recorded_time

    ###############################################################################
    # get_all_measurement_names: method to fetch the names of all the measurements
    # param - id_list: list of the measurement ids
    # returns: list of measurement names for the given ids.
    def get_measurement_name_list(self, id_list):
        conn = self.getDBConn()
        cursor = conn.cursor()

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
        except Exception as e:
            return {'error': e.args[1]}
        finally:
            cursor.close()
            conn.close()
        return measurement_names

    ###############################################################################

    # get_measurement_name: method to fetch the name of the measurements of the
    # param - given measurement_id: id of a measurement
    # returns: name of the measurement for the given id
    def get_measurement_name(self, measurement_id):
        conn = self.getDBConn()
        cursor = conn.cursor()
        query_name = ("SELECT name "
                      "FROM measurement_types "
                      "WHERE id = %s;")
        try:
            cursor.execute(query_name, (measurement_id,))
            measurement_name, = cursor.fetchall()
        except Exception as e:
            return {'error': e.args[1]}
        finally:
            cursor.close()
            conn.close()
        return measurement_name

    ###############################################################################

    # get_measurements: method to fetch measurements for multiple systems
    # param system list of system_id
    # param measurements list of measurements
    # return dictionary with system_id as key and list of measurements[timestamp,m1,m2,...]
    # with key as the measurement
    def get_measurements(self, systems, measurements,status_id):
        conn = self.getDBConn()
        payload = {}
        values = {}
        cursor = conn.cursor()
        try:
            for system in systems:
                time_range_response = self.get_time_ranges_for_status(system,status_id);

                if time_range_response:
                    query = self.create_measurement_query(system, measurements,time_range_response)
                    cursor.execute(query)
                    payload[system] = cursor.fetchall()
                else:
                    print "No status found in the system_status table for system: :" + system + \
                          "  status: " + str(status_id)
                    payload[system] = ()

        except Exception as e:
            return {'error': e.args[1] + "system: :" + str(systems) + "  measurements: " + str(measurements)}
        finally:
            cursor.close()
            conn.close()

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
    # create_measurement_query: method to create query to fetch measurements from a system
    # param system system_id
    # param measurements list of measurements
    # return query
    @staticmethod
    def create_measurement_query(system, measurements,time_ranges):
        query = ""
        for i in range(0, len(measurements)):
            # query += """select {prefix}, {prefix}.time as time,
            #             {prefix}.value as value from aqxs_{prefix}_{system}
            #             {prefix} where """.format(prefix=measurements[i], system=system)


            query += "select \'" + measurements[i] + "\'," + measurements[i] + ".time as time," \
                         + measurements[i] + ".value as value from aqxs_" + measurements[i] + "_" + system \
                         + " " + measurements[i] + " where "
            if time_ranges:
                for j in range(0,len(time_ranges)):
                     start_time = "'" + str(time_ranges[j][0]) + "'"
                     end_time = "'" + str(time_ranges[j][1]) + "'"

                     if j == len(time_ranges) - 1:
                         query += "( time > " + start_time + " and time < " + end_time + ")"
                     else:
                         query += "( time > " + start_time + " and time < " + end_time + ") or"

            else:
                query += "1=1"

            if i == len(measurements) - 1:
                query += " order by time "
            else:
                query += " union "

        return query

    ###############################################################################
    # get_time_ranges_for_status: method to get the time range for measurements for
    #                            a  system_uid for a phase
    # param system_id the system's unique id
    # param status_id status_id for system
    # returns the start time and end time for measurements for a given system_uid
    #  and status
    def get_time_ranges_for_status(self,system_id,status_id):
        conn = self.getDBConn()
        cursor = conn.cursor()
        query_time_ranges = ("select start_time, end_time from system_status"  \
                             + " where system_uid = %s"
                             + " and sys_status_id = %s" )
        try:
            cursor.execute(query_time_ranges,(system_id,status_id,))
            time_ranges = cursor.fetchall()
        except Exception as e:
            return {'error': e.args[1]}
        finally:
            cursor.close()
            conn.close()
        return time_ranges

    ###############################################################################


    def get_status_type(self, status_id):
        conn = self.getDBConn()
        cursor = conn.cursor()
        query_name = ("SELECT status_type "
                      "FROM status_types "
                      "WHERE id = %s")
        try:
            cursor.execute(query_name, (status_id,))
            status_type = cursor.fetchall()
            status_type = str(status_type[0][0])
        except Exception as e:
            return {'error': e.args[1]}
        finally:
            cursor.close()
            conn.close()
        return status_type

    ###############################################################################
    # get_all_measurement_info: method to fetch the id, name, units, min and max
    #                           of all the measurements
    # returns the id, name, units, min, max of all the measurements
    ###############################################################################
    def get_all_measurement_info(self):
        conn = self.getDBConn()
        cursor = conn.cursor()
        query_mea_info = ("SELECT * "
                          "FROM measurement_types;")
        try:
            cursor.execute(query_mea_info)
            measurement_info = cursor.fetchall()
        except Exception as e:
            return {'error': e.args[1]}
        finally:
            cursor.close()
            conn.close()
        return measurement_info

    ###############################################################################
    # get_annotations: method to fetch annotations for multiple systems
    # param system list of system_id
    # returns dictionary with system_id as key and list of annotations[annotation_id,timestamp]

    def get_annotations(self, systems):
        conn = self.getDBConn()
        annotations = {}
        cursor = conn.cursor()
        try:
             system_id_list_str = self.form_in_list(systems)

             query =  "select s.system_uid, annotation_id, timestamp from system_annotations sa" + \
                      " join systems s on" + \
                      " s.id = sa.system_id" +\
                      " where s.system_uid in " + system_id_list_str + \
                      " order by s.system_uid,timestamp"

             cursor.execute(query)
             annotations_fetched = cursor.fetchall()

             for s in systems:
                 annotations[s] = []

             for annotation in annotations_fetched:
                 system_id = annotation[0]
                 annotations[system_id].append(annotation)

             return annotations

        except Exception as e:
            return {'error': e.args[1] + "system: :" + str(systems)}
        finally:
            cursor.close()
            conn.close()

    ###############################################################################
    # form_in_list: method to form the the "in" string from given list
    # param id_list list of system_ids
    # returns the string formed from the given id_list

    def form_in_list(self,id_list):
        id_list_str = "("
        for i in range(0, len(id_list)):
            id_list_str = id_list_str + "'" + id_list[i] + "',"

        id_list_str = list(id_list_str)
        id_list_str[len(id_list_str) - 1] = ")"

        id_list_str = ''.join(id_list_str)
        return id_list_str

