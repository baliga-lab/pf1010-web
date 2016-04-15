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


    def getReadableAnnotations(self):
        cursor = self.conn.cursor()

        query = ('SELECT a.id, a.annotation_key, a.annotation_desc '
                 'FROM annotations a ')

        try:
            cursor.execute(query)
            results = cursor.fetchall()
        except:
            raise
        finally:
            cursor.close()

        return results


    def addAnnotation(self, annotation):
        cursor = self.conn.cursor()

        systemID = annotation['systemID'],
        annotationID = annotation['annotationID']
        timestamp = annotation['timestamp']

        query = ('INSERT INTO system_annotations sa (system_id, annotation_id, timestamp)'
                 'VALUES (%s, %s, %s)')

        values = (systemID, annotationID, timestamp)

        try:
            cursor.execute(query, values)
            self.conn.commit()
        except:
            self.conn.rollback()
            raise
        finally:
            cursor.close()

        return cursor.lastrowid


    def getAnnotationsForSystem(self, systemID):
        cursor = self.conn.cursor()

        query = ('SELECT a.annotation_key, a.annotation_value, a.annotation_desc, sa.timestamp '
                 'FROM system_annotations sa '
                 'LEFT JOIN annotations a ON sa.annotation_id = a.id'
                 'WHERE sa.system_id = %s ')

        try:
            cursor.execute(query, (systemID,))
            result = cursor.fetchall()
        except:
            raise
        finally:
            cursor.close()

        return result
