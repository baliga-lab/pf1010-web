from ..dao.systemsDAO import SystemsDAO
import json

#data analysis and viz data access api
class DavAPI:

    #method to get all system data
    #param conn : db connection
    def get_all_systems(self, conn):
       # Fetch all the systems
       s = SystemsDAO(conn)
       systems=s.get_systems()

       # Create a list of systems
       systems_list = []
       for system in systems:

           # For each system, create a JSON
           obj = {'system_id': system[0],
                  'user_id': str(system[1]),
                  'latitude': str(system[2]),
                  'longitude': str(system[3])}

           systems_list.append(json.dumps(obj))


       # Print JSON on console
       #print json.dumps({'systems' : systems_list})
       # Return the JSON
       return json.dumps({'systems' : systems_list})