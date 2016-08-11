# DAO for systems table
import MySQLdb
class SystemsDAO:

    def __init__(self, app):
        self.app = app

    def getDBConn(self):
        return MySQLdb.connect(host=self.app.config['HOST'], user=self.app.config['USER'],
                               passwd=self.app.config['PASS'], db=self.app.config['DB'])
    ###############################################################################
    # get_system_name(system_uid) - It takes in the system_uid as the input
    #                            parameter and returns the metadata for the
    #                            given system. Currently, it returns only
    #                            the name of the system.
    # param system_uid : system's UID
    def get_system_name(self, system_uid):
        conn = self.getDBConn()
        cursor = conn.cursor()
        query = "SELECT name FROM systems WHERE system_uid = %s"

        try:
            cursor.execute(query, (system_uid,))
            result, = cursor.fetchall()
        except Exception as e:
            error = {'error': e.message}
            return error
        finally:
            cursor.close()
            conn.close()

        return result[0]

    ###############################################################################
    # get_all_systems_info() - It returns the system information as a JSON
    #                          object.
    def get_all_systems_info(self):
        conn = self.getDBConn()
        cursor = conn.cursor()
        query = ("SELECT s.system_uid, s.user_id, s.name, s.start_date, s.location_lat, location_lng, "
                 "s.status,"
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
            conn.close()

        return rows
