class annotationDAO:

    def __init__(self, conn):
        self.conn = conn

    def getReadableAnnotation(self, annotationID):
        cursor = self.conn.cursor()

        query = ('SELECT a.annotation_key, a.annotation_desc '
                 'FROM annotations a '
                 'WHERE a.id = %s ')

        try:
            cursor.execute(query, (annotationID,))
            result = cursor.fetchone()
        except:
            raise
        finally:
            cursor.close()

        return result