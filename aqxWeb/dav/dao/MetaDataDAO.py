# DAO for fetching all filtering metadata
import MySQLdb

class MetadataDAO:

    def __init__(self, app):
        self.app = app

    def getDBConn(self):
        return MySQLdb.connect(host=self.app.config['HOST'], user=self.app.config['USER'],
                               passwd=self.app.config['PASS'], db=self.app.config['DB'])
    # get_all_filters - It returns all the metadata that are needed
    #                   to filter the displayed systems.
    def get_all_filters(self):
        conn = self.getDBConn()
        cursor = conn.cursor()
        query_filters = ("select \'crops\', c.name from crops c union "
                         "select \'aqx_techniques\' , aqt.name  from aqx_techniques aqt union "
                         "select \'aqx_organisms\', ao.name  from aquatic_organisms ao union "
                         "select \'growbed_media\', gbm.name  from growbed_media gbm union "
                         "select \'status_types\', concat(id,':',status_type) as name  from status_types;")
        try:
            cursor.execute(query_filters)
            aqx_techniques = cursor.fetchall()
        finally:
            cursor.close()
            conn.close()
        return aqx_techniques
