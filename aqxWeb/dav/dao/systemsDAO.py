#DAO for systems table

def SystemsDAO():

    #constructor
    def __init__(self, conn):
        self.conn = conn

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