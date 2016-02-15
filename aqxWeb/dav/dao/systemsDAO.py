# DAO for systems table

class SystemsDAO:
    # constructor
    def __init__(self, conn):
        self.conn = conn

    # method to get all systems from database
    def get_systems(self):
        cursor = self.conn.cursor();
        query = ("select system_uid, user_id, location_lat ,location_lng "
                 "from systems")

        try:
            cursor.execute(query)
            rows = cursor.fetchall()

        finally:
            cursor.close()
            self.conn.close()

        return rows

    # method to get the metadata of a given system from the database
    def get_metadata(self, system_ui):
        cursor = self.conn.cursor()
        query = "SELECT name FROM systems WHERE system_uid = %s"



        try:
            cursor.execute(query, (system_ui, ))
            result, = cursor.fetchall()

        finally:
            cursor.close()
            self.conn.close()

        return result

    # method to get the metadata of all the systems
    def get_all_systems_info(self):
        cursor = self.conn.cursor()
        query = ("SELECT s.system_uid, s.user_id, s.name, s.start_date, "
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
