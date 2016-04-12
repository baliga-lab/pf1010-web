class userDAO:

    def __init__(self, conn):
        self.conn = conn

    def hasUser(self, googleID):
        cursor = self.conn.cursor()

        query = ('SELECT COUNT(1) '
                 'FROM users u '
                 'WHERE u.googleID_id = %s')

        try:
            cursor.execute(query, (googleID,))
            result = cursor.fetchone()
        except:
            return 'Error getting user'
        finally:
            cursor.close()

        return result

    def getUserID(self, googleID):
        cursor = self.conn.cursor()

        query = ('SELECT u.id '
                 'FROM users u '
                 'WHERE u.google_id = %s ')

        try:
            cursor.execute(query, (googleID,))
            result = cursor.fetchone()
        except:
            return 'Error getting user'
        finally:
            cursor.close()

        return result
