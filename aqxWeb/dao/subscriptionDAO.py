class subscriptionDAO:

    def __init__(self, conn):
        self.conn = conn

    def subscribe(self, email):
        print('here')
        print(email)
        cursor = self.conn.cursor()

        query = ('INSERT INTO subscriptions (email) VALUES (%s)')

        try:
            cursor.execute(query, (email,))
            self.conn.commit()
        except:
            raise
        finally:
            cursor.close()

        return cursor.lastrowid