# DAO for systems table
import datetime
import json
import uuid
from flask import session
from datetime import datetime
from flask import current_app

class SystemsDAO:

    # constructor
    def __init__(self, conn):
        self.conn = conn

    ###############################################################################
    # get_metadata(system_uid) - It takes in the system_uid as the input
    #                            parameter and returns the metadata for the
    #                            given system.
    # param system_uid : system's UID
    def get_metadata(self, system_uid):
        cursor = self.conn.cursor()

        query = ("SELECT s.system_uid, s.user_id, s.name, s.start_date, s.location_lat, s.location_lng, "
                 "aqt.name as 'aqx_technique', "
                 "gm.name as 'growbed_media', "
                 "cr.name as 'crop_name', "
                 "sc.num as 'crop_count', "
                 "ao.name as 'organism', "
                 "sao.num as 'organism_count', "
                 "s.creation_time, "
                 "s.status "
                 "FROM systems s "
                 "sao.num as 'organism_count' "
                 "FROM systems s "
                 "LEFT JOIN aqx_techniques aqt ON s.aqx_technique_id = aqt.id "
                 "LEFT JOIN system_crops sc    ON s.id = sc.system_id "
                 "LEFT JOIN crops cr           ON sc.crop_id = cr.id "
                 "LEFT JOIN system_gb_media sgm    ON s.id = sgm.system_id "
                 "LEFT JOIN growbed_media gm       ON sgm.gb_media_id = gm.id "
                 "LEFT JOIN system_aquatic_organisms sao ON s.id = sao.system_id "
                 "LEFT JOIN aquatic_organisms ao ON  sao.organism_id= ao.id "
                 "WHERE s.system_uid = %s "
                 )

        #query = "SELECT name FROM systems WHERE system_uid = %s"

        try:
            cursor.execute(query, (system_uid,))
            result = cursor.fetchall()

        finally:
            cursor.close()
            self.conn.close()

        return result

    ###############################################################################
    # get_all_systems_info() - It returns the system information as a JSON
    #                          object.
    def get_all_systems_info(self):
        cursor = self.conn.cursor()
        query = ("SELECT s.system_uid, s.user_id, s.name, s.start_date, s.location_lat, s.location_lng,"
                 "aqt.name as 'aqx_technique', "
                 "gm.name as 'growbed_media', "
                 "cr.name as 'crop_name', "
                 "sc.num as 'crop_count', "
                 "ao.name as 'organism', "
                 "sao.num as 'organism_count', "
                 "s.creation_time, "
                 "s.status "
                 "FROM systems s "
                 "LEFT JOIN aqx_techniques aqt ON s.aqx_technique_id = aqt.id "
                 "LEFT JOIN system_crops sc    ON s.id = sc.system_id "
                 "LEFT JOIN crops cr           ON sc.crop_id = cr.id "
                 "LEFT JOIN system_gb_media sgm    ON s.id = sgm.system_id "
                 "LEFT JOIN growbed_media gm       ON sgm.gb_media_id = gm.id "
                 "LEFT JOIN system_aquatic_organisms sao ON s.id = sao.system_id "
                 "LEFT JOIN aquatic_organisms ao ON  sao.organism_id= ao.id;")

        try:
            cursor.execute(query)
            rows = cursor.fetchall()

        finally:
            cursor.close()
            self.conn.close()

        return rows

    ###############################################################################

    def get_system_by_system_uid(self, system_uid):
        cursor = self.conn.cursor()
        query = ('select * from systems_ui where system_uid = %s ')
        try:
            cursor.execute(query, (system_uid,))
            system = cursor.fetchall()
        finally:
            cursor.close()
        return system

    def get_system_by_id(self, id):
        cursor = self.conn.cursor()
        query = ('select * from systems_ui where id = %s ')
        try:
            cursor.execute(query, (id,))
            system = cursor.fetchall()
        finally:
            cursor.close()
        return system

    def get_system_by_name(self, name):
        cursor = self.conn.cursor()
        query = ('select * from systems_ui where name = %s ')
        try:
            cursor.execute(query, (name,))
            system = cursor.fetchall()
        finally:
            cursor.close()
        return system




    ###############################################################################
    #     create_system() - takes in a system json object and adds this system into the list of all systems
    #     argument system is a form object

    def create_system(self, system):
        old_system = self.get_system_by_name(system.get('name'))
        if len(old_system) != 0:
            return "System exists"
        cursor = self.conn.cursor()
        ###insert into projectfeed.systems (id, user_id, name, start_date, status, aqx_technique_id,creation_time,location_lat,location_lng,state)
        ###values(111, 111, 'zhibo', date('1977 - 6 - 14'), 0, 1, timestamp('2015-08-11 04:48:21'), 111, 111, 'PRE-ESTABLISHED');
        ###this query works in mysql  date timestamp use ''

        #test purpose with hard data and it worked!
        # system ={
        #     #'id' : 222, itis auto generated so it is removed from query
        #     #'user_id': 222,   #it can be got from session     session['uid']
        #     'name': 'zhibo-TEST',
        #     #'system_uid': 222222,
        #     'start_date': '1988-09-09',
        #     'aqx_technique_id': 1,
        #     'creation_time': '2015-08-11 04:48:21',
        #     'location_lat': 0,
        #     'location_lng': 0
        # }


        query = ('insert into systems_ui (user_id, name, system_uid,start_date, aqx_technique_id,'
                 'creation_time,location_lat,location_lng) '
                 'values(%s,%s,%s,%s,%s,now(),%s,%s); ')
        data = (session['uid'],system.get('name'),str(uuid.uuid1().hex),
                system.get('start_date'),system.get('aqx_technique_id'),
                system.get('location_lat'), system.get('location_lng'))

        try:
            cursor.execute(query,data)
            self.conn.commit()
        except:
            self.conn.rollback()
            cursor.close()
            return "Insert error"
        finally:
            cursor.close()
        return "System inserted"


    #get_all_user_systems : returns a user's all systems
    def get_all_user_systems(self, user_id):
        cursor = self.conn.cursor()
        query = ('select * from systems where user_id = %s ')

        try:
            cursor.execute(query, (user_id,))
            rows = cursor.fetchall()

        finally:
            cursor.close()
            self.conn.close()

        return rows

    def new_system_id(self):
        """Generates a new system id"""
        return uuid.uuid1().hex

    def get_all_measurement_type_names(self):
        cursor = self.conn.cursor()
        query = ('select name from measurement_types ')

        try:
            cursor.execute(query)
            rows = cursor.fetchall()

        finally:
            cursor.close()
            self.conn.close()

        return rows


    def create_table_measurement(self,name,system):
        cursor = self.conn.cursor()
        query = "create table if not exists %s ( time timestamp primary key not null, value decimal(13,10) not null )" % \
                self.measurement_table_name(name, system.get('system_uid'))
                #self.measurement_table_name(name, '111')


        cursor.execute(query)


        # cursor = self.conn.cursor()
        # query = "create table if not exists %s (time timestamp primary key not null, value decimal(13,10) not null)" \
        #         % self.meas_table_name(system.get('system_uid'), name)
        #
        # try:
        #     cursor.execute(query)
        #     table = cursor.fetchall()
        #
        # finally:
        #     cursor.close()
        #     self.conn.close()
        #
        # return table


    def measurement_table_name(self, measurement_type_name, system_uid):
        return "aqxs_%s_%s" % (measurement_type_name, system_uid)

    def delete_system_with_system_uid(self, system_uid):
        cursor = self.conn.cursor()
        query = ('delete from systems_ui where system_uid = %s limit 1 ')
        try:
            cursor.execute(query, (system_uid,))
            self.conn.commit()
        finally:
            cursor.close()
        return str(1)

    def delete_measurement_tables_with_system_uid(self, system_uid):
        cursor = self.conn.cursor()
        query = 'drop table if exists %s '
        ATTR_NAMES = {'ammonium', 'o2', 'ph', 'nitrate', 'light', 'temp', 'nitrite', 'chlorine',
                      'hardness', 'alkalinity'}
        try:
            for name in ATTR_NAMES:
                cursor.execute(query, (self.measurement_table_name(name, system_uid),))

            self.conn.commit()
        finally:
            cursor.close()
        return str(1)