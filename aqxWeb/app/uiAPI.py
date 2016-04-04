
from UserDAO import UserDAO
from systemsDAO import SystemsDAO
from MetaDataDAO import MetadataDAO
from metasystemsDAO import MetaSystemsDAO
#from aqxWeb.dao.systemsDAO import SystemsDAO
#from aqxWeb.dao.MetaDataDAO import MetadataDAO
#from aqxWeb.dao.metasystemsDAO import MetaSystemsDAO
from collections import defaultdict
import json




# user interface data access api


class UiAPI:

    def __init__(self, conn):
        self.conn = conn
        self.sys = SystemsDAO(self.conn)
        self.user = UserDAO(self.conn)
        self.metaData = MetadataDAO(self.conn)
        self.metaSys = MetaSystemsDAO(self.conn)

    ###############################################################################
    # get_system_metadata
    ###############################################################################
    # param conn : db connection
    # param system_id : system id
    # get_system_metadata(system_uid) - It takes in the system_uid as the input
    #                                   parameter and returns the metadata for the
    #                                   given system.

    # def get_system_metadata(self, system_id):
    #     s = SystemsDAO(self.conn)
    #     sys = s.get_metadata(system_id)
    #     if 'error' in sys:
    #         return json.dumps(sys)
    #     system = sys[0]
    #     obj = {'system_uid': system[0],
    #            'user_id': system[1],
    #            'system_name': system[2],
    #            'start_date': str(system[3]),
    #            'lat': str(system[4]),
    #            'lng': str(system[5]),
    #            'aqx_technique_name': system[6],
    #            'growbed_media': system[7],
    #            'crop_name': system[8],
    #            'crop_count': system[9],
    #            'organism_name': system[10],
    #            'organism_count': system[11]}
    #
    #     return json.dumps({'system': str(obj)})

    ###############################################################################
    #         get_system_with_system_id
    ###############################################################################
    # param conn : db connection
    # param system_id : system id
    #         get_system_with_system_id(system_uid) - It takes in the system_uid as the input
    #                                   parameter and returns the metadata for the
    #                                   given system.

    def get_system_with_system_id(self, system_id):
        systems = self.sys.get_all_systems_info()
        if 'error' in systems:
            return json.dumps(systems)
        #systems[0] is a system json
        #return json.dumps({'system': str(systems[0][0])})  which is system id
        for system in systems:
            if system[0] == system_id:
                obj = {'system_uid': str(system[0]),
                       'user_id': system[1],
                       'system_name': str(system[2]),
                       'start_date': str(system[3]),
                       'lat': str(system[4]),
                       'lng': str(system[5]),
                       'aqx_technique_name': str(system[6]),
                       'growbed_media': system[7],
                       'crop_name': str(system[8]),
                       'crop_count': system[9],
                       'organism_name': str(system[10]),
                       'organism_count': system[11]}
                return json.dumps({'system': str(obj)})
        return json.dumps({'system': 'not found'})




    ###############################################################################
    # get_all_systems_info
    ###############################################################################
    # param conn : db connection
    # get_all_systems_info() - It returns the system information as a JSON
    #                          object.

    def get_all_systems_info(self):
        systems = self.sys.get_all_systems_info()
        if 'error' in systems:
            return json.dumps(systems)

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

    def get_all_filters_metadata(self):
        results = self.metaData.get_all_filters()
        if 'error' in results:
            return json.dumps(results)
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

    def get_user(self, user_id):
        u = UserDAO(self.conn)
        result_temp = u.get_user(user_id)
        if 'error' in result_temp:
            return json.dumps(result_temp)
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
    # fetch existing user data
    ###############################################################################
    # param conn : db connection
    # param user_id : user's google id
    # get_user_with_google_id - It returns user details using google id.

    def get_user_with_google_id(self, google_id):
        u = UserDAO(self.conn)
        result_temp = u.get_user_by_google_id(google_id)
        if 'error' in result_temp:
            return json.dumps(result_temp)
        result = result_temp[0]
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

    def put_user(self, user):
        u = UserDAO(self.conn)
        result = u.put_user(user)
        message = {
            "message": result
        }
        return json.dumps({'status': message})


    ###############################################################################
    # insert user data
    ###############################################################################
    # param conn : db connection
    # param user : user details in the form of a json structure
    # insert_user - It inserts the user details into the users table

    def insert_user(self, user):
        u = UserDAO(self.conn)
        result = u.put_user(user)
        message = {
            "message" : result
        }
        return json.dumps({"status": message})


    ###############################################################################
    # get_all_systems
    ###############################################################################
    # param conn : db connection
    # get_all_systems() - It returns List of all aquaponics systems, system_uid,name,user_id owning
    # the system longitude and latitude of system's location as a JSON object.

    def get_systems(self):
        systems = self.sys.get_all_systems_info()
        if 'error' in systems:
            return json.dumps(systems)

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


    ###############################################################################
    # check_system_exists
    ###############################################################################
    # param conn : db connection, system_uid
    # check_system_exists() - It returns "If system exists:
    #{"status":"True"}
    #If system does not exist:
    #{"status":"False"}

    def check_system_exists(self, system_uid):
        systems = self.sys.get_all_systems_info()
        if 'error' in systems:
            return json.dumps(systems)
        for system in systems:
            if system[0] == system_uid:
                return json.dumps({"status": str(True)})
        return json.dumps({"status": str(False)})