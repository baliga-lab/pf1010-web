from datetime import datetime
# DAO for aqx_techniques table


class UserDAO:
    # constructor to get connection
    def __init__(self, conn):
        self.conn = conn

    # method to get user information
    def get_user(self, user_id):
        cursor = self.conn.cursor()
        query = ("select id,google_id,email,default_site_location_lat,"
                 "default_site_location_lng from users where google_id = %s")
        try:
            cursor.execute(query, (user_id,))
            users = cursor.fetchall()
        finally:
            cursor.close()
        return users

    # method to put user information
    def put_user(self, user):

        old_user = self.get_user(user.get('googleid'))
        if len(old_user) != 0:
            return "User exists"
        cursor = self.conn.cursor()
        query = ("insert into users (google_id, email,creation_time,status ,"
                 "default_site_location_lat,default_site_location_lng)    "
                 "values(%s,%s,%s, %s,%s,%s);")
        data = (user.get('googleid'), user.get('email'), datetime.now(), 0
                                   , user.get('lat'), user.get('long'));
        try:
            cursor.execute(query, data)
            self.conn.commit()
        except:
            self.conn.rollback()
            cursor.close()
            return "Insert error"
        finally:
            cursor.close()
        return "User inserted"

    # method to delete user information
    def delete_user(self, user_id):

        cursor = self.conn.cursor()
        query = ("delete from users where google_id = %s")
        try:
            cursor.execute(query, (user_id,))
            self.conn.commit()
        except:
            print "del bad"
            self.conn.rollback()
            cursor.close()
            return "delete error"
        finally:
            cursor.close()
        return "User deleted"
