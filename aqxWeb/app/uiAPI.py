
from aqxWeb.dao.UserDAO import UserDAO
from aqxWeb.dao.systemsDAO import SystemsDAO
from aqxWeb.dao.MetaDataDAO import MetadataDAO
from aqxWeb.dao.systemImageDAO import SystemImageDAO
from aqxWeb.dao.systemAnnotationDAO import SystemAnnotationDAO
from collections import defaultdict
import json




# user interface data access api


class UiAPI:

    def __init__(self, conn):
        self.conn = conn
        self.sys = SystemsDAO(self.conn)
        self.user = UserDAO(self.conn)
        self.metaData = MetadataDAO(self.conn)

    ###############################################################################
    # get_system_metadata
    ###############################################################################
    # param conn : db connection
    # param system_id : system id
    # get_system_metadata(system_uid) - It takes in the system_uid as the input
    #                                   parameter and returns the metadata for the
    #                                   given system.


    def get_system_metadata(self, system_id):
        # i wanna use get_metadata to directly get that system, but not work. maybe query is wrong
        # so i choose to use get_system_with_system_id below
        s = SystemsDAO(self.conn)
        system = s.get_metadata(system_id)
        if 'error' in system:
            return json.dumps(system)
        clean_sys = str(system)[2:-2]


        # obj = {'system_uid': str(system[0]),
        #        'user_id': system[1],
        #        'system_name': str(system[2]),
        #        'start_date': str(system[3]),
        #        'lat': str(system[4]),
        #        'lng': str(system[5]),
        #        'aqx_technique_name': str(system[6]),
        #        'growbed_media': system[7],
        #        'crop_name': str(system[8]),
        #        'crop_count': system[9],
        #        'organism_name': str(system[10]),
        #        'organism_count': system[11],
        #        'creation_time': str(system[12]),
        #        'status': system[13],
        #        'state': str(system[14])
        #        }

        return json.dumps({'system': str(system)})

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
                       'organism_count': system[11],
                       'creation_time': str(system[12]),
                       'status': system[13],
                       'id': system[14]
                      }
                return json.dumps({'system': obj})
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
                   'organism_count': system[11],
                   'creation_time': str(system[12]),
                   'status': system[13],
                   'id': system[14]}

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

    ###############################################################################
    #     create_system
    # input: system, a form object
    # if json is in this order, then json[0] should be system_uid
    # system_uid, user_id, name, start_date, status, aqx_technique_id
    # technique on add system page is the actual technique, but db needs that technique's id
    ###############################################################################
    def create_system(self, system):
        s = SystemsDAO(self.conn)
        result = s.create_system(system)
        # system_crops = s.create_system_crops_table(system)
        # system_gb_media = s.create_system_gb_media(system)
        # system_aquatic_organisms = s.create_system_aquatic_organisms(system)
        ATTR_NAMES = {'ammonium', 'o2', 'ph', 'nitrate', 'light', 'temp', 'nitrite', 'chlorine',
                      'hardness', 'alkalinity'}
        for name in ATTR_NAMES:
            s.create_table_measurement(name, system)
        message = {
            "message": result
        }
        return json.dumps({'status': message})

    ###############################################################################
    #   get_all_user_systems
    #   get a user's all systems
    ###############################################################################
    def get_all_user_systems(self, user_id):
        s = SystemsDAO(self.conn)
        result = s.get_all_user_systems(user_id)
        if 'error' in result:
            return json.dumps(result)
        systems_list = []
        for system in result:
            # For each system, create a system
            obj = {'id': system[0],
                   'user_id': system[1],
                   'name': system[2],
                   'system_uid': system[3],
                   'creation_time': str(system[4]),
                   'start_date': str(system[5]),
                   'aqx_technique_id': system[6],
                   'status': system[7],
                   'lat': str(system[8]),
                   'lng': str(system[9]),
                    'state': system[10]}

            systems_list.append(obj)

        return json.dumps({'systems': systems_list})

    # add an image to a syetem
    # id is auto incremented
    def add_image_to_system(self, system_uid, image):
        s = SystemImageDAO(self.conn)
        result = s.add_image_to_system(system_uid, image)
        message = {
            "message": result
        }
        return json.dumps({'status': message})

    # delete an image from a system
    def delete_image_from_system(self, system_uid, image_id):
        s = SystemImageDAO(self.conn)
        result = s.delete_image_from_system(system_uid, image_id)
        message = {
            "message": result
        }
        return json.dumps({'status': message})

    # view image of a system
    def view_image_from_system(self, system_uid, image_id):
        s = SystemImageDAO(self.conn)
        image = s.view_image_from_system(system_uid, image_id)
        if 'error' in image:
            return json.dumps(image)
        obj = {'id': image[0],
               'system_id': image[1],
               'image_url': image[2]}
        return json.dumps({'image': obj})

    # get a system's all images

    def get_system_all_images(self, system_uid):
        s = SystemImageDAO(self.conn)
        result = s.get_system_all_images(system_uid)
        if 'error' in result:
            return json.dumps(result)
        images_list = []
        for image in result:
            # For each system, create a system
            obj = {'id': image[0],
                   'system_id': image[1],
                   'image_url': image[2]}
            images_list.append(obj)

        return json.dumps({'images': images_list})

    # add an annotation to a system
    def add_annotation(self, system_uid, annotation):
        s = SystemAnnotationDAO(self.conn)
        result = s.add_annotation(system_uid, annotation)
        message = {
            "message": result
        }
        return json.dumps({'status': message})

    # get a system's all annotations
    def view_annotation(self,system_uid):
        s = SystemAnnotationDAO(self.conn)
        result = s.view_annotation(system_uid)
        if 'error' in result:
            return json.dumps(result)
        annotations_list = []
        for annotation in result:
            # For each system, create a system
            obj = {'id': annotation[0],
                   'system_id': annotation[1],
                   'water': annotation[2],
                   'pH': str(annotation[3]),
                   'harvest': str(annotation[4]),
                   'plant': str(annotation[5]),
                   'fish': annotation[6],
                   'bacteria': annotation[7],
                   'cleanTank': annotation[8],
                   'reproduction': annotation[9],
                   'timestamp': annotation[10]}
            annotations_list.append(obj)

        return json.dumps({'annotations': annotations_list})

    # delete a row of systems table with the given system_uid and the associated 10 measurement tables
    def delete_metadata(self,system_uid):
        s = SystemsDAO(self.conn)
        result = s.delete_system_with_system_uid(system_uid)
        result_for_measurement_tables = s.delete_measurement_tables_with_system_uid(system_uid)
        if 'error' in result:
            return json.dumps(result)
        return json.dumps({'system_deleted?': result})

    # get system id, not system_uid for sc api call
    def get_system_id_and_system_uid_with_user_id_and_system_name(self, user_id, name):
        systems = self.sys.get_all_systems_info()
        if 'error' in systems:
            return json.dumps(systems)

        for system in systems:
            if str(system[1]) == user_id and str(system[2]) == name:
                obj = {
                    'system_id': system[14],
                    'system_uid': system[0]
                }
                # print json.loads(json.dumps({'system': obj}))['system']['system_id']
                # print json.loads(json.dumps({'system': obj}))['system']['system_uid']
                return json.dumps({'system': obj})
        return json.dumps({'system_id': 'not found'})

    # get status by given system uID
    def get_status_by_system_uid(self, system_uid):
        systems = self.sys.get_all_systems_info()
        if 'error' in systems:
            return json.dumps(systems)
        for system in systems:
            if system[0] == system_uid:
                obj = {
                       'status': system[13]
                       }
                return json.dumps({'system': obj})
        return json.dumps({'system': 'not found'})

    # system gb media table
    def create_system_gb_media_table(self, system_gb_media_json):
        try:

            s = SystemsDAO(self.conn)
            result = s.create_system_gb_media_table(system_gb_media_json)
            message = {
                "message": result
            }
            return json.dumps({'status': message})
        except Exception as ex:
            print "Exception : " + str(ex.message)

    # system crops table
    def create_system_crop_table(self, system_crop_json):
        try:

            s = SystemsDAO(self.conn)
            result = s.create_system_crop_table(system_crop_json)
            message = {
                "message": result
            }
            return json.dumps({'status': message})
        except Exception as ex:
            print "Exception : " + str(ex.message)

    # system_aquatic_organisms table
    def create_system_quatic_organisms_table(self, system_aquatic_organisms_json):
        try:

            s = SystemsDAO(self.conn)
            result = s.create_system_quatic_organisms_table(system_aquatic_organisms_json)
            message = {
                "message": result
            }
            return json.dumps({'status': message})
        except Exception as ex:
            print "Exception : " + str(ex.message)