from aqxWeb.dav.dao.systemsDAO import SystemsDAO
from aqxWeb.dav.dao.MetaDataDAO import MetadataDAO
from aqxWeb.dav.dao.UserDAO import UserDAO
from collections import defaultdict
import json


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

    def get_user(self, conn, user_id):
        u = UserDAO(conn)
        result = u.get_user(user_id)
        user = {
            "id" : result[0],
            "google_id" : result[1],
            "email" : result[2],
            "latitude" : str(result[3]),
            "longitude" :str(result[4])
        }
        return json.dumps({'user': user})

    ###############################################################################
    # insert user data
    ###############################################################################

    def put_user(self, conn, user):
        u = UserDAO(conn)
        result = u.put_user(user)
        message = {
            "message" : result
        }
        return json.dumps({'status': message})

