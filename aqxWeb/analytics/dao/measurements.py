# DAO for fetching all the data related to the measurements of the systems
import MySQLdb
import traceback
import datetime as dt
from flask import current_app
from math import floor

class MeasurementsDAO:

    def __init__(self, app):
        self.app = app

    def getDBConn(self):
        return MySQLdb.connect(host=self.app.config['HOST'], user=self.app.config['USER'],
                               passwd=self.app.config['PASS'], db=self.app.config['DB'])

    def get_all_measurement_names(self):
        conn = self.getDBConn()
        cursor = conn.cursor()
        query_names = ("SELECT name,full_name "
                       "FROM measurement_types;")
        try:
            cursor.execute(query_names)
            return [(name, full_name) for name, full_name in cursor.fetchall()]
        except Exception as e:
            return {'error': e.args[1]}
        finally:
            cursor.close()
            conn.close()


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

    def get_measurement_types(self, id_list):
        conn = self.getDBConn()
        cursor = conn.cursor()
        query = "SELECT name FROM measurement_types where id in (%s)" % ",".join(map(str, id_list))

        try:
            cursor.execute(query)
            return cursor.fetchall()
        finally:
            cursor.close()
            conn.close()


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

    def get_measurements(self, systems, measurements, status_id):
        conn = self.getDBConn()
        payload = {}
        cursor = conn.cursor()
        try:
            for system in systems:
                time_range_response = self.get_time_ranges_for_status(system, status_id)

                if time_range_response:
                    query = self.create_measurement_query(system, measurements,time_range_response)
                    cursor.execute(query)
                    payload[system] = cursor.fetchall()
                else:
                    current_app.logger.warn("No status found in the system_status table for system: %s status: %s",
                                            system, str(status_id))
                    payload[system] = ()
        finally:
            cursor.close()
            conn.close()

        # create new list for each measurement
        values = {s: {m: [] for m in measurements} for s in systems}
        for s in systems:
            v = payload[s]
            if v:
                for m in v:
                    values[s][m[0]].append(m)

        return values


    ###############################################################################
    # return the count of all measurement records for the given system and measurement
    # param - system_uid: UID identifying an aquaponic system
    # param - measurement: Name of the measurement for which data is requested
    # returns: A dict {'count': <count of all rows>} that contains the total number of records
    #          for the given system and measurement
    def get_data_count(self, system_uid, measurement):
        conn = self.getDBConn()
        cursor = conn.cursor()
        table_name = 'aqxs_' + measurement + '_' + system_uid
        payload = {}
        try:
            query = "SELECT COUNT(*) FROM %s" % table_name
            cursor.execute(query)
            result = cursor.fetchone()
            payload['count'] = result[0]
        except Exception as e:
            return {'error': e.args[1]}
        finally:
            cursor.close()
            conn.close()
        return payload


    ###############################################################################
    # return all measurement data for a given system and measurement
    # param - system_uid: UID identifying an aquaponic system
    # param - measurement: Name of the measurement for which data is requested
    # param - page: the page for which data is requested. Pages are based on items_per_page
    # returns: A dict of the given page of data for the given system and measurement
    #          the returned dict contains 'data' which is the list of measurements
    #          and 'total_pages' which is the total page count for this system/measurement
    def get_all_measurements(self, system_uid, measurement, page):
        conn = self.getDBConn()
        cursor = conn.cursor()

        # Prep some values for the query
        items_per_page = 20
        page = int(page)
        start = items_per_page * (page - 1)
        table_name = 'aqxs_' + measurement + '_' + system_uid

        # Declare and initialize the payload
        payload = {'data': []}

        try:
            # Retrieve records in time order, descending (most recent first)
            query = "SELECT * FROM %s ORDER BY time DESC LIMIT %%s OFFSET %%s " % table_name
            cursor.execute(query, (items_per_page, start))
            result = list(cursor.fetchall())
            # Figure out total number of pages. We return this with every request
            total_count = self.get_data_count(system_uid, measurement)
            total_pages = int(floor(total_count['count'] / items_per_page) + 1)

            # Error if page not in range
            if total_pages < page:
                raise ValueError('The provided page number  ' + str(page)
                                 + ' is out of range. There allowable range is [1,%d]' % total_pages)

            # Add the page count
            payload['total_pages'] = total_pages

            # Loop through the query result, coerce the result strings to datetime and float
            # Turn the results into dicts of form {time: <datetime>, value: <float>}
            for r in result:
                updated_at = r[2].strftime('%Y-%m-%d %H:%M:%S') if r[2] else None
                payload['data'].append({'time': r[0].strftime('%Y-%m-%d %H:%M:%S'), 'value': float(r[1]), 'updated_at': updated_at})
        except Exception as e:
            print e
            return {'error': str(e)}
        finally:
            cursor.close()
            conn.close()
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
        query_time_ranges = ("select start_time, end_time from system_status" \
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
                     " s.id = sa.system_id" + \
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

    ###############################################################################
    # get_measurement: Returns a specific measurement for a system, by it's creation time
    # param system_uid - UID of the system
    # param measurement - Name of the measurement type
    # param created_at - Creation time to ID the requested measurement
    # returns the string formed from the given id_list

    def get_measurement(self, system_uid, measurement, created_at):

        conn = self.getDBConn()
        cursor = conn.cursor()
        table_name = 'aqxs_' + measurement + '_' + system_uid

        # Declare and initialize the payload
        payload = {'created_at': '', 'value': ''}

        try:
            # Retrieve records in time order, descending (most recent first)
            query = "SELECT * FROM %s WHERE time = %%s " % table_name
            cursor.execute(query, [created_at])
            data = cursor.fetchone()

            if not data or len(data) == 0:
                raise ValueError("No data found for the given creation time.")

            payload['created_at'] = data[0].strftime('%Y-%m-%d %H:%M:%S')
            payload['value'] = float(data[1])

        except Exception as e:
            print e
            return {'error': str(e)}
        finally:
            cursor.close()
            conn.close()
        return payload


    ###############################################################################
    # get_measurement: Returns a specific measurement for a system, by it's creation time
    # param system_uid - UID of the system
    # param measurement - Name of the measurement type
    # param created_at - Creation time to ID the requested measurement
    # returns the string formed from the given id_list

    def update_existing_measurement(self, system_uid, measurement, data):
        conn = self.getDBConn()
        cursor = conn.cursor()
        table_name = 'aqxs_' + measurement + '_' + system_uid
        try:
            query = "UPDATE %s SET time=%%s, value=%%s, updated_at=%%s WHERE time=%%s" % table_name
            result = cursor.execute(query, (data['time'],  data['value'], data['updated_at'], data['time']))
            conn.commit()
        except Exception as e:
            print e
            return {'error': str(e)}
        finally:
            cursor.close()
            conn.close()
        return 'Successfully updated ' + str(result) + ' records(s)!'
