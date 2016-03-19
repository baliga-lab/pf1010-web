from aqxWeb.dao.metasystemsDAO import MetaSystemsDAO
from aqxWeb.dao.MetaDataDAO import MetadataDAO
from aqxWeb.dao.UserDAO import UserDAO
from collections import defaultdict
import json


# user interface data access api


class uiAPI:

    ###############################################################################
    # get_system_metadata
    ###############################################################################
    # param conn : db connection
    # param system_id : system id
    # get_system_metadata(system_uid) - It takes in the system_uid as the input
    #                                   parameter and returns the metadata for the
    #                                   given system.

    def get_system_metadata(self, conn, system_id):
        s = MetaSystemsDAO(conn)
        result = s.get_metadata(system_id)

        return json.dumps({'system': result})

    ###############################################################################
    # get_all_systems_info
    ###############################################################################
    # param conn : db connection
    # get_all_systems_info() - It returns the system information as a JSON
    #                          object.

    def get_all_systems_info(self, conn):
        s = MetaSystemsDAO(conn)
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
    # fetch fetch existing user data
    ###############################################################################
    # param conn : db connection
    # param user_id : user's google id
    # get_user - It returns user details based on google id.

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
    # fetch existing user data
    ###############################################################################
    # param conn : db connection
    # param user_id : user's google id
    # get_user_with_google_id - It returns user details using google id.

    def get_user_with_google_id(self, conn, google_id):
        u = UserDAO(conn)
        result = u.get_user(google_id)
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
    # insert user data
    ###############################################################################
    # param conn : db connection
    # param user : user details in the form of a json structure
    # insert_user - It inserts the user details into the users table

    def insert_user(self, conn, user):
        u = UserDAO(conn)
        result = u.put_user(user)
        message = {
            "message" : result
        }
        return json.dumps({"status": message})


    ###############################################################################
    # get_all_systems
    ###############################################################################
    # param conn : db connection
    # get_all_systems() - It returns List of all aquaponics systems, system_uid,name,user_id owning the system
    #longitude and latitude of system's location as a JSON object.

    def get_all_systems(self, conn):
        s = MetaSystemsDAO(conn)
        systems = s.get_all_systems_info()

        # Create a list of systems
        systems_list = []
        for system in systems:
            # For each system, create a system
            obj = {"system_uid": system[0],
                   "user_id": system[1],
                   "system_name": system[2],
                   "lat": str(system[3]),
                   "lng": str(system[4])}

            systems_list.append(obj)

        return json.dumps({'systems': systems_list})






