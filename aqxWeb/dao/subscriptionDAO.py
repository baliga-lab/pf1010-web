import MySQLdb

class subscriptionDAO:
    def __init__(self, app):
        self.app = app

    def getDBConn(self):
        return MySQLdb.connect(host=self.app.config['HOST'], user=self.app.config['USER'],
                               passwd=self.app.config['PASS'], db=self.app.config['DB'])

    def subscribe(self, email):
        conn = self.getDBConn()
        print('here')
        print(email)
        cursor = conn.cursor()

        query = ('INSERT INTO subscriptions (email) VALUES (%s)')

        try:
            cursor.execute(query, (email,))
            conn.commit()
        except:
            raise
        finally:
            cursor.close()
            conn.close()
        return cursor.lastrowid