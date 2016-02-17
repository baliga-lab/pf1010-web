# DAO for aqx_techniques table


class MetadataDAO:
    # constructor to get connection
    def __init__(self, conn):
        self.conn = conn

    # method to get the filtering criteria
    def get_all_filters(self):
        cursor = self.conn.cursor()
        query_filters = ("select \'crops\', c.name from crops c union "
                         "select \'aqx_techniques\' , aqt.name  from aqx_techniques aqt union "
                         "select \'aqx_organisms\', ao.name  from aquatic_organisms ao union "
                         "select \'growbed_media\', gbm.name  from growbed_media gbm;")
        try:
            cursor.execute(query_filters)
            aqx_techniques = cursor.fetchall()
        finally:
            cursor.close()
            self.conn.close()
        return aqx_techniques
