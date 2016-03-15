# DAO for systems table


class SystemsDAO:

    # constructor
    def __init__(self, conn):
        self.conn = conn

    ###############################################################################
    # get_metadata(system_uid) - It takes in the system_uid as the input
    #                            parameter and returns the metadata for the
    #                            given system. Currently, it returns only
    #                            the name of the system.
    # param system_uid : system's UID
    def get_metadata(self, system_uid):
        cursor = self.conn.cursor()
        query = "SELECT name FROM systems WHERE system_uid = %s"

        try:
            cursor.execute(query, (system_uid,))
            result, = cursor.fetchall()

        finally:
            cursor.close()
            self.conn.close()

        return result

    ###############################################################################
    # get_all_systems_info() - It returns the system information as a JSON
    #                          object.
    def get_all_systems_info(self):
        cursor = self.conn.cursor()
        query = ("SELECT s.system_uid, s.user_id, s.name, s.start_date, s.location_lat, location_lng, "
                 "aqt.name as 'aqx_technique', "
                 "gm.name as 'growbed_media', "
                 "cr.name as 'crop_name', "
                 "sc.num as 'crop_count', "
                 "ao.name as 'organism', "
                 "sao.num as 'organism_count' "
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
     ###############################################################################
    # get_system_name() - It returns the system names of all the input system_uid
    def get_system_name(self,system_id_list):
        cursor = self.conn.cursor()

        system_id_list_str = "("
        for i in range(1, len(system_id_list)):
            system_id_list_str = system_id_list_str + system_id_list[i] + ","

        system_id_list_str[len(system_id_list_str) -1 ] = ")"


        query = ("select s.system_uid,s.name "
                 "from systems s "
                 "where s.system_uid  in " +
                  system_id_list_str)

        print query

        try:
            cursor.execute(query)
            rows = cursor.fetchall()

        finally:
            cursor.close()
            self.conn.close()

        return rows