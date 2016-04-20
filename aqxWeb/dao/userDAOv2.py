import MySQLdb

class userDAO:
    def __init__(self, app):
        self.app = app

    def getDBConn(self):
        return MySQLdb.connect(host=self.app.config['HOST'], user=self.app.config['USER'],
                               passwd=self.app.config['PASS'], db=self.app.config['DB'])

    def hasUser(self, googleID):
        conn = self.getDBConn()
        cursor = conn.cursor()

        query = ('SELECT COUNT(1) '
                 'FROM users u '
                 'WHERE u.googleID_id = %s')

        try:
            cursor.execute(query, (googleID,))
            result = cursor.fetchone()
        except:
            raise
        finally:
            cursor.close()
            conn.close()
        return result


    def getUserID(self, googleID):
        conn = self.getDBConn()
        cursor = conn.cursor()

        query = ('SELECT u.id '
                 'FROM users u '
                 'WHERE u.google_id = %s ')

        try:
            cursor.execute(query, (googleID,))
            result = cursor.fetchone()
        except:
            raise
        finally:
            cursor.close()
            conn.close()
        return result


    def createUser(self, googleProfile):
        conn = self.getDBConn()
        cursor = conn.cursor()

        query = ('INSERT INTO users (google_id, email)'
                 'VALUES (%s, %s)')

        values = (googleProfile.id, googleProfile.email)

        try:
            cursor.execute(query, values)
            conn.commit()
        except:
            conn.rollback()
            raise
        finally:
            cursor.close()
            conn.close()

        return cursor.lastrowid


    def deleteUser(self, userID):
        conn = self.getDBConn()
        cursor = conn.cursor()

        query = ('DELETE FROM users u '
                 'WHERE u.id = %s '
                 'LIMIT 1')

        try:
            cursor.execute(query, (userID,))
            conn.commit()
        except:
            conn.rollback()
            raise
        finally:
            cursor.close()
            conn.close()
        return True
