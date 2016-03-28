from datetime import datetime
# DAO for users table


class UserDAO:
    # constructor to get connection
    def __init__(self, conn):
        self.conn = conn

    ###############################################################################
    # get_user(user_id) - method to fetch user details
    # param user_id : users google id

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

    ###############################################################################
    # put_user(user) - method to insert user details(create new user)
    # param user : json structure with user information

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

    ###############################################################################
    # delete_user(user_id) - method to delete user details(cleanup for unit testing)
    # param user_id : user id of the user

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
