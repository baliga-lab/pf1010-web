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
            "message" : result
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
        # Create a list to store the latest values of all the measurements
        latest_values = []
        # For each measurement
        for name in names:
            # Fetch the name of the measurement using regular expression
            measurement_name = (re.findall(r"\(u'(.*?)',\)", str(name))[0])
            if measurement_name != 'time':
                # As each measurement of a system has a table on it's own,
                # we need to create the name of each table.
                # Each measurement table is: aqxs_measurementName_systemUID
                table_name = "aqxs_" + measurement_name + "_" + system_uid
                # Get the latest value stored in the table
                value = m.get_latest_value(table_name)
                # Append the value to the latest_value[] list
                latest_values.append(value)
        obj = {
            'system_uid': str(system_uid),
            'alkalinity': str(latest_values[0]),
            'ammonium': str(latest_values[1]),
            'chlorine': str(latest_values[2]),
            'hardness': str(latest_values[3]),
            'light': str(latest_values[4]),
            'nitrate': str(latest_values[5]),
            'nitrite': str(latest_values[6]),
            'o2': str(latest_values[7]),
            'ph': str(latest_values[8]),
            'temp': str(latest_values[9])
        }
        return json.dumps(obj)

