from datetime import datetime
import MySQLdb
# DAO for users table


class UserDAO:
    # constructor to get connection
    def __init__(self, app):
        self.app = app

    def getDBConn(self):
        return MySQLdb.connect(host=self.app.config['HOST'], user=self.app.config['USER'],
                               passwd=self.app.config['PASS'], db=self.app.config['DB'])



    ###############################################################################
    # get_user(user_id) - method to fetch user details
    # param user_id : users google id

    def get_user_by_google_id(self, user_id):
        conn = self.getDBConn()
        cursor = conn.cursor()
        query = ("select id,google_id,email,default_site_location_lat,"
                 "default_site_location_lng from users where google_id = %s")
        try:
            cursor.execute(query, (user_id,))
            users = cursor.fetchall()
        finally:
            cursor.close()
            conn.close()
        return users

        ###############################################################################
        # get_user(user_id) - method to fetch user details
        # param user_id : users user id

    def get_user(self, user_id):
        conn = self.getDBConn()
        cursor = conn.cursor()
        query = ("select id,google_id,email,default_site_location_lat,"
                 "default_site_location_lng from users where id = %s")
        try:
            cursor.execute(query, (user_id,))
            users = cursor.fetchall()
        finally:
            cursor.close()
            conn.close()
        return users

    ###############################################################################
    # put_user(user) - method to insert user details(create new user)
    # param user : json structure with user information

    def put_user(self, user):
        conn = self.getDBConn()
        old_user = self.get_user_by_google_id(user.get('googleid'))
        if len(old_user) != 0:
            return "User exists"
        cursor = conn.cursor()
        query = ("insert into users (google_id, email,creation_time,status ,"
                 "default_site_location_lat,default_site_location_lng)    "
                 "values(%s,%s,%s, %s,%s,%s);")
        data = (user.get('googleid'), user.get('email'), datetime.now(), 0
                                   , user.get('lat'), user.get('long'));
        try:
            cursor.execute(query, data)
            conn.commit()
        except:
            conn.rollback()
            cursor.close()
            return "Insert error"
        finally:
            cursor.close()
            conn.close()
        return "User inserted"

    ###############################################################################
    # delete_user(user_id) - method to delete user details(cleanup for unit testing)
    # param user_id : user id of the user

    def delete_user(self, user_id):
        conn = self.getDBConn()
        cursor = conn.cursor()
        query = ("delete from users where google_id = %s")
        try:
            cursor.execute(query, (user_id,))
            conn.commit()
        except:
            print "del bad"
            conn.rollback()
            cursor.close()
            return "delete error"
        finally:
            cursor.close()
            conn.close()
        return "User deleted"
