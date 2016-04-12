class mailingListDAO:
    def __init__(self, conn):
        self.conn = conn

    def addEmail(self, email):
        cursor = self.conn.cursor()

        query = ('INSERT INTO mailing_list (email)'
                 'VALUES (%s)')

        values = email

        try:
            cursor.execute(query, values)
        except:
            raise
        finally:
            cursor.close()

        return cursor.lastrowid