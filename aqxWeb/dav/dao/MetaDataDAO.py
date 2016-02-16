# DAO for aqx_techniques table


class MetadataDAO:
    # constructor to get connection
    def __init__(self, conn):
        self.conn = conn

    # method to get the filtering criteria
    def get_all_filters(self):
        cursor = self.conn.cursor()
        query_filters = ("select \'crop\', c.name from crops c union "
                         "select \'technique\' , aqt.name  from aqx_techniques aqt union "
                         "select \'organism\', ao.name  from aquatic_organisms ao union "
                         "select \'gbmedia\', gbm.name  from growbed_media gbm;")
        try:
            cursor.execute(query_filters)
            aqx_techniques = cursor.fetchall()
        finally:
            cursor.close()
            self.conn.close()
        return aqx_techniques
