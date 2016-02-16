from aqxWeb.dav.dao.systemsDAO import SystemsDAO
from aqxWeb.dav.dao.MetaDataDAO import MetadataDAO
from collections import defaultdict
import json


# data analysis and viz data access api


class DavAPI:


    ###############################################################################
    # get_systems
    # Fetches all the systems with its location and its user_id
    ###############################################################################
    # param conn : db connection
    def get_all_systems(self, conn):
        # Fetch all the systems
        s = SystemsDAO(conn)
        systems = s.get_systems()

        # Create a list of systems
        systems_list = []
        for system in systems:
            # For each system, create a JSON
            obj = {'system_id': system[0],
                   'user_id': str(system[1]),
                   'latitude': str(system[2]),
                   'longitude': str(system[3])}

            systems_list.append(json.dumps(obj))

        return json.dumps({'systems': systems_list})

    ###############################################################################
    # get_system_metadata
    ###############################################################################
    # param conn : db connection
    # param system_id : system id
    def get_system_metadata(self, conn, system_id):
        s = SystemsDAO(conn)
        result = s.get_metadata(system_id)

        return result

    ###############################################################################
    # get_all_systems_info
    ###############################################################################
    # param conn : db connection
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

    def get_all_filters_metadata(self, conn):
        m = MetadataDAO(conn)
        results = m.get_all_filters()
        vals = defaultdict(list)
        for result in results:
            type = result[0]
            value = result[1]
            vals[type].append(value)
        return json.dumps({'filters': vals})
