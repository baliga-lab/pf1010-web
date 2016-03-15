from aqxWeb.dav.dao.MeasurementsDAO import MeasurementsDAO
from aqxWeb.dav.dao.systemsDAO import SystemsDAO
from aqxWeb.dav.dao.MetaDataDAO import MetadataDAO
from aqxWeb.dav.dao.UserDAO import UserDAO
from collections import defaultdict
import json
import re


# data analysis and viz data access api


class DavAPI:

    ###############################################################################
    # get_system_metadata
    ###############################################################################
    # param conn : db connection
    # param system_id : system id
    # get_system_metadata(system_uid) - It takes in the system_uid as the input
    #                                   parameter and returns the metadata for the
    #                                   given system. Currently, it returns only
    #                                   the name of the system.

    def get_system_metadata(self, conn, system_id):
        s = SystemsDAO(conn)
        result = s.get_metadata(system_id)

        return result

    ###############################################################################
    # get_all_systems_info
    ###############################################################################
    # param conn : db connection
    # get_all_systems_info() - It returns the system information as a JSON
    #                          object.

    def get_all_systems_info(self, conn):
        s = SystemsDAO(conn)
        systems = s.get_all_systems_info()

        # Create a list of systems
        systems_list = []
        for system in systems:
            # For each system, create a system
            obj = {'system_uid': system[0],
                   'user_id': system[1],
                   'system_name': system[2],
                   'start_date': str(system[3]),
                   'lat': str(system[4]),
                   'lng': str(system[5]),
                   'aqx_technique_name': system[6],
                   'growbed_media': system[7],
                   'crop_name': system[8],
                   'crop_count': system[9],
                   'organism_name': system[10],
                   'organism_count': system[11]}

            systems_list.append(obj)

        return json.dumps({'systems': systems_list})

    ###############################################################################
    # fetches all filter criteria
    ###############################################################################
    # param conn : db connection
    # get_all_filters_metadata - It returns all the metadata that are needed
    #                            to filter the displayed systems.

    def get_all_filters_metadata(self, conn):
        m = MetadataDAO(conn)
        results = m.get_all_filters()
        vals = defaultdict(list)
        for result in results:
            type = result[0]
            value = result[1]
            vals[type].append(value)
        return json.dumps({'filters': vals})

    ###############################################################################
    # fetch user data
    ###############################################################################
    # param conn : db connection
    # param user_id : user's google id
    # get_user - It returns user details based on google id.

    def get_user(self, conn, user_id):
        u = UserDAO(conn)
        result_temp = u.get_user(user_id)
        result = result_temp[0]
        user = {
            "id" : result[0],
            "google_id": result[1],
            "email": result[2],
            "latitude": str(result[3]),
            "longitude":str(result[4])
        }
        return json.dumps({'user': user})

    ###############################################################################
    # insert user data
    ###############################################################################
    # param conn : db connection
    # param user : user details in the form of a json structure
    # get_user - It inserts the user details into the users table

    def put_user(self, conn, user):
        u = UserDAO(conn)
        result = u.put_user(user)
        message = {
            "message": result
        }
        return json.dumps({'status': message})

    ###############################################################################
    # fetch latest recorded values of measurements for a given system
    ###############################################################################
    # param conn : db connection
    # param system_uid : system's unique ID
    # get_system_measurements - It returns the latest recorded values of the
    #                           given system.

    def get_system_measurements(self, conn, system_uid):
        m = MeasurementsDAO(conn)
        # Fetch names of all the measurements
        names = m.get_all_measurement_names()
        # Create a list to store the name, latest time and value of all the measurements
        x = []
        # For each measurement
        for name in names:
            # Fetch the name of the measurement using regular expression
            measurement_name = self.get_measurement_name(name)
            if measurement_name != 'time':
                # As each measurement of a system has a table on it's own,
                # we need to create the name of each table.
                # Each measurement table is: aqxs_measurementName_systemUID
                table_name = self.get_measurement_table_name(measurement_name, system_uid)
                # Get the latest value stored in the table
                value = m.get_latest_value(table_name)
                # Append the value to the latest_value[] list
                if len(value) == 1:
                    value_temp = value[0]
                    temp = {
                        'name': measurement_name,
                        'time': str(value_temp[0]),
                        'value': str(value_temp[1])
                    }
                else:
                    temp = {
                        'name': measurement_name,
                        'time': None,
                        'value': None
                    }

                x.append(temp)

        obj = {
            'system_uid': str(system_uid),
            'measurements': x
        }
        return json.dumps(obj)

    ###############################################################################
    # Get name of the measurement
    ###############################################################################
    # Fetch the name of the measurement using regular expression
    # param: 'name' retrieved from the measurement_types table
    @staticmethod
    def get_measurement_name(name):
        return re.findall(r"\(u'(.*?)',\)", str(name))[0]


    ###############################################################################
    # Get name of the measurement table for a given system
    ###############################################################################
    # As each measurement of a system has a table on it's own,
    # we need to create the name of each table.
    # Each measurement table is: aqxs_measurementName_systemUID
    # param: measurement_name: name of the measurement
    # param: system_uid: system's unique ID
    @staticmethod
    def get_measurement_table_name(measurement_name, system_uid):
        table_name = "aqxs_" + measurement_name + "_" + system_uid
        return table_name

    ###############################################################################
    # fetch latest recorded values of given measurement for a given system
    ###############################################################################
    # param conn : db connection
    # param system_uid : system's unique ID
    # param measurement_id: ID of a measurement
    # get_system_measurement - It returns the latest recorded values of the
    #                           given system.
    def get_system_measurement(self, conn, system_uid, measurement_id):
        m = MeasurementsDAO(conn)
        # Fetch the name of the measurement
        measurement = m.get_measurement_name(measurement_id)
        measurement_name = self.get_measurement_name(measurement)
        # Create the name of the table
        table_name = self.get_measurement_table_name(measurement_name, system_uid)
        # Get the latest value recorded in that table
        result = m.get_latest_value(table_name)
        result_temp = result[0]
        obj = {
            'system_uid': system_uid,
            'time': str(result_temp[0]),
            'value': str(result_temp[1])
        }
        return json.dumps(obj)

    ###############################################################################
    # Retrieve the readings for input system and type of measurements
    ###############################################################################
    # param conn : db connection
    # param system_uid_list : List of system unique IDs
    # param measurement_type_list: List of measurement_IDs
    # get_system_measurement - It returns the readings of all the input system uids
    #                          for all input measurement ids
    def get_readings_for_plot(self,conn, system_uid_list, measurement_type_list):
        m = MeasurementsDAO(conn)

        system_uid_list = ["555d0cfe9ebc11e58153000c29b92d09"]
        measurement_type_list = ["o2","ph","light"]
        response = m.get_measurements(system_uid_list,measurement_type_list)

        system_measurement_list = []

        for system_uid in system_uid_list:
            readings = response[system_uid]
            system_measuremnt_json = self.form_system_measuremnt_json(self,system_uid,readings,measurement_type_list)
            system_measurement_list.append(system_measuremnt_json)

        return json.dumps({'response': system_measurement_list})

    ###############################################################################
    # form the system's measurement reading
    ###############################################################################
    @staticmethod
    def form_system_measuremnt_json(self,system_uid,readings,measurement_type_list):
        measurement_list = []
        valueList = []
        for measurement_type in measurement_type_list:
            valueList = self.form_values_list(measurement_type,readings)

            measurement = {
                "type" : measurement_type,
                "values": valueList
            }
            measurement_list.append(measurement)

        system_measurement = {
            "system_uid" : system_uid,
            "measurement": measurement_list
        }
        return system_measurement

    ###############################################################################
    # form the list of values
    ###############################################################################
    @staticmethod
    def form_values_list(measurement_type,readings):
        valuesList=[]
        for reading in readings:
            if reading[0] == measurement_type:
                print reading[1]
                print reading[2]
                values={
                    "y": str(reading[2]),
                    "date": str(reading[1])
                }
                valuesList.append(values)

        return valuesList