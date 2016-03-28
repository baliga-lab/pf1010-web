
from django.core.serializers.json import DjangoJSONEncoder

from aqxWeb.dav.dao.MeasurementsDAO import MeasurementsDAO
from aqxWeb.dav.dao.systemsDAO import SystemsDAO
from aqxWeb.dav.dao.MetaDataDAO import MetadataDAO
from aqxWeb.dav.dao.UserDAO import UserDAO
from collections import defaultdict
import json
import re
import random
import datetime


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

    def __init__(self, conn):
        self.conn = conn
        self.sys = SystemsDAO(self.conn)
        self.met = MetadataDAO(self.conn)
        self.mea = MeasurementsDAO(self.conn)


    def get_system_metadata(self,system_id):
        s = SystemsDAO(self.conn)
        result = s.get_metadata(system_id)

        return result

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
    # get_all_filters_`data - It returns all the metadata that are needed
    #                            to filter the displayed systems.

    def get_all_filters_metadata(self):
        results = self.met.get_all_filters()
        if 'error' in results:
            return json.dumps(results)
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
    # fetch latest recorded values of measurements for a given system
    ###############################################################################
    # param conn : db connection
    # param system_uid : system's unique ID
    # get_system_measurements - It returns the latest recorded values of the
    #                           given system.

    def get_system_measurements(self, system_uid):
        # Fetch names of all the measurements
        names = self.mea.get_all_measurement_names()
        if 'error' in names:
            return json.dumps(names)
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

                num_of_records = 1
                # Get the latest value stored in the table
                value = self.mea.get_latest_value(table_name, num_of_records)
                if 'error' in value:
                    return json.dumps(value)
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
    def get_system_measurement(self,system_uid, measurement_id):
        # Fetch the name of the measurement
        measurement = self.mea.get_measurement_name(measurement_id)
        if 'error' in measurement:
                    return json.dumps(measurement)
        #measurement_name = self.get_measurement_name(measurement)
        if measurement[0] == 'light':
            num_of_records = 7
        else:
            num_of_records = 1
        # Create the name of the table
        table_name = self.get_measurement_table_name(measurement[0], system_uid)
        # Get the latest value recorded in that table
        result = self.mea.get_latest_value(table_name, num_of_records)
        if 'error' in result:
                    return json.dumps(result)
        values = []
        for result_temp in result:
            values_temp = {
                'time': str(result_temp[0]),
                'value': str(result_temp[1])
            }
            values.append(values_temp)
        obj = {
            'system_uid': system_uid,
            'records': values
        }
        return json.dumps(obj)

    ###############################################################################
    # Insert records values of given measurement for a given system
    ###############################################################################
    # param conn : db connection
    # param system_uid : system's unique ID
    # param measurement_id: ID of a measurement
    # get_system_measurement - It returns the latest recorded values of the
    #                           given system.
    def put_system_measurement(self, data):
        # Fetch the name of the measurement
        system_uid = data.get('system_uid')
        measurement_id = data.get('measurement_id')
        time = data.get('time')
        value = data.get('value')
        measurement = self.mea.get_measurement_name(measurement_id)
        if 'error' in measurement:
                    return json.dumps(measurement)
        measurement_name = self.get_measurement_name(measurement)
        # Create the name of the table
        table_name = self.get_measurement_table_name(measurement_name, system_uid)
        result = self.mea.put_system_measurement(table_name, time, value)
        if 'error' in result:
                    return json.dumps(result)
        message = {
            "message": result
        }
        return json.dumps({'status': message})

    ###############################################################################
    # Retrieve the readings for input system and type of measurements
    ###############################################################################
    # param system_uid_list : List of system unique IDs
    # param measurement_id_list: List of measurement_IDs
    # get_readings_for_plot - It returns the readings of all the input system uids
    #                         for all input measurement ids
    def get_readings_for_plot(self,system_uid_list,measurement_id_list):
        # Form a list of names from the list of ids
        measurement_type_list = self.mea.get_measurement_name_list(measurement_id_list)

        # Return if there is any error in getting the measurement type names
        if 'error' in measurement_type_list:
                    error_msg = measurement_type_list
                    return json.dumps(error_msg )

        # If there is no type for given id throw an exception
        if not measurement_type_list:
            error_msg = "No data found for " + "measurement_id_list: " + str(measurement_id_list)
            raise ValueError(error_msg)

        # Returned list is list of tuples. Separating measurement type names from tuple
        measurement_name_list  = []
        for name in measurement_type_list:
             measurement_name_list.append(str(name[0]))

        # Retrieve the measurements calling DAO
        data_retrieved = self.mea.get_measurements(system_uid_list,measurement_name_list)
        if 'error' in data_retrieved:
            return json.dumps(data_retrieved)

        system_measurement_list = []

        for system_uid in system_uid_list:
            readings = data_retrieved[system_uid]
            system_measurement_json = self.form_system_measurement_json(system_uid,readings,
                                                                         measurement_name_list)
            system_measurement_list.append(system_measurement_json)

        return json.dumps({"response": system_measurement_list})


    ###############################################################################
    # Form the system's measurement reading json
    ###############################################################################
    # param system_uid  : Unique id of system
    # param readings    : all readings for the input system_uid
    # param measurement_type_list : list of measurement types in the request
    # form_system_measurement_json  - It returns the json for all information needed
    # for the plot for the input system_uid
    #
    def form_system_measurement_json(self,system_uid,readings,measurement_type_list):
        measurement_list = []

        # For each measurement type, form the list of readings
        for measurement_type in measurement_type_list:

            valueList=[]

            if readings:
                if readings[measurement_type]:
                    valueList = self.form_values_list(self,measurement_type,readings[measurement_type])
                else:
                    valueList=[]

            measurement = {
                "type" : measurement_type,
                "values": valueList
            }
            measurement_list.append(measurement)
        system_measurement = {
            "system_uid" : system_uid,
            "name" : self.sys.get_system_name(system_uid),
            "measurement": measurement_list
        }

        return system_measurement

    ###############################################################################
    # Form the list of values
    ###############################################################################
    # param measurement_type : name of the type of measurement
    # param all_readings : readings associated with input measurement_type
    # form_values_list   : It returns the list of readings formed from input
    # readings. ALl the readings that fall in 1-hour bucket from time of first reading
    # are averaged and readings is timestamped with latest timestamp in the bucket.
    @staticmethod
    def form_values_list(self,measurement_type,all_readings):
        valuesList=[]

        # Initialize the variables
        startDate = all_readings[0][1]
        prev_reading = all_readings[0]
        prevX = 0
        # Required variable for averaging
        sum = 0
        counter = 0

        # Every time  'values' is formed for previous reading if it falls outside the bucket, otherwise averaging is
        # done, over the bucket

        for i in range (1,len(all_readings) + 1):
            try:
                # This condition takes care of the last reading, which gets left out
                if(i == len(all_readings)):
                    # By incrementing x deliberately, we enforce the 'values' formation for the very last reading
                    reading = prev_reading
                    x = prevX + 1
                # This condition takes care of all but the last reading
                else:
                    reading = all_readings[i]
                    curDate = reading[1]
                    # Calculate the difference in hours from previous reading
                    x = self.calc_diff_hours(curDate,startDate)
                # If x >  prevX, build the values object and append to the values list
                if x > prevX:

                    # If counter > 0, there were readings from 1-hour bucket and values should be averaged
                    if(counter > 0):
                        sum =  sum + prev_reading[2]
                        counter = counter + 1

                        avg= sum / counter
                        lastValDate = prev_reading[1]

                        values= self.build_values(prevX,avg,lastValDate)

                        # Reset Average in a 1-hour bucket params
                        sum = 0
                        counter = 0
                    # Otherwise, simply build values from previous reading
                    else:
                        y = prev_reading[2]
                        values = self.build_values(prevX,y, prev_reading[1])

                    #   Append the current values to valuelist
                    valuesList.append(values)

                    prev_reading = reading
                    prevX = x

                else:
                     # if reading falls in same bucket, accumulate the reading value to average later
                     if x == prevX:
                        sum =  sum + prev_reading[2]
                        counter = counter + 1
                        prevX = x
                        prev_reading = reading
                     # Skip the reading if the readings are not in order. This is unlikely to occur.
                     else:
                         print("Skipped Value for ",measurement_type,curDate)

            except ValueError as err:
                raise ValueError('Error in preparing values list',measurement_type,reading)

        return valuesList
    ###############################################################################
    # Build the values object
    ###############################################################################
    # param x : x value of reading
    # param y  : y value of reading
    # param reading_date  : date of reading
    #  build_values - It returns the values object formed from x,y and reading date
    @staticmethod
    def build_values(x,y,reading_date):
        values={
                    "x": x,
                    "y": round(y,2),
                    "date": str(reading_date)
                }
        return values

    ###############################################################################
    # Get the system name
    ###############################################################################
    # param conn : db connection
    # param  system_id : Unique id of the system
    # get_system_name  - It returns the name of the system
    #
    @staticmethod
    def get_system_name(conn,system_id):
        s = SystemsDAO(conn)
        return s.get_system_name(system_id)

    ###############################################################################
    # Calculate the difference in hours
    ###############################################################################
    # param curDate    : date of current reading
    # param  startDate : date of first reading
    # calc_diff_hours  : It returns the difference in hours between two input dates
    @staticmethod
    def calc_diff_hours(curDate,startDate):
        if(curDate < startDate ):
            raise ValueError('Current date is lesser than previous date',curDate,startDate)
        else:
            diff = curDate - startDate
            return diff.days*24 + diff.seconds/3600


    ###############################################################################
    # get all measurement types
    ###############################################################################
    # returns all types that can be chosen for the axes of the graph

    def get_all_measurement_names(self):
        meas = self.mea.get_all_measurement_names()
        if 'error' in meas:
                    return json.dumps(meas)
        mlist = []
        for m in meas:
            mlist.append(m)
        mlist.append('time')
        return json.dumps({"types":mlist})



    ################################################################################
    # method to generate test data
    # param conn - connection to db
    # param minrange - minimum value u want to insert
    # param maxrange - maximum value u want to insert
    # systems - list of systems
    # meas - list of measurements
    ################################################################################

    def generate_data(self,minrange,maxrange,systems,meas):
        for s in systems:
            d = datetime.datetime(2015,1,1,0,0,0)
            for i in range(1,6,1):
                for j in range(0,24,1):
                    d = datetime.datetime(2015,1,i,j,0,0)
                    for m in meas:
                        d = datetime.datetime(2015,1,i,j,0,0)
                        table_name = self.get_measurement_table_name(m, s)
                        time = d.strftime('%Y-%m-%d %H:%M:%S')
                        val = random.uniform(minrange,maxrange)
                        self.mea.put_system_measurement(table_name,time,val)

    ###############################################################################
    # get all measurement information: id, name, units, min, max
    ###############################################################################
    # returns all types

    def get_all_measurement_info(self):
        meas = self.mea.get_all_measurement_info()
        if 'error' in meas:
                    return json.dumps(meas)
        measurement_names = {}
        for m in meas:
            measurement_names[m[1]] = {}
            measurement_names[m[1]]["id"] = (m[0])
            measurement_names[m[1]]["unit"] = (m[2])
            measurement_names[m[1]]["min"] = (m[3])
            measurement_names[m[1]]["max"] = (m[4])
        return json.dumps({"measurement_info": measurement_names}, cls=DjangoJSONEncoder)

