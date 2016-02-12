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
