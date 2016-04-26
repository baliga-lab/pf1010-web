import MySQLdb

class annotationDAO:
    def __init__(self, app):
        self.app = app

    def getDBConn(self):
        return MySQLdb.connect(host=self.app.config['HOST'], user=self.app.config['USER'],
                               passwd=self.app.config['PASS'], db=self.app.config['DB'])

    def getReadableAnnotation(self, annotationID):
        conn = self.getDBConn()
        cursor = conn.cursor()

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
            conn.close()
        return result


    def getReadableAnnotations(self):
        conn = self.getDBConn()
        cursor = conn.cursor()

        query = ('SELECT a.id, a.annotation_key, a.annotation_desc '
                 'FROM annotations a ')

        try:
            cursor.execute(query)
            results = cursor.fetchall()
        except:
            raise
        finally:
            cursor.close()
            conn.close()
        return results


    def addAnnotation(self, annotation):
        conn = self.getDBConn()
        cursor = conn.cursor()

        systemID = annotation['systemID']
        annotationID = annotation['annotationID']
        timestamp = annotation['timestamp']

        query = ('INSERT INTO system_annotations (system_id, annotation_id, timestamp) '
                 'VALUES (%s, %s, %s)')

        values = (systemID, annotationID, timestamp)

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


    def getAnnotationsForSystem(self, systemID):
        conn = self.getDBConn()
        cursor = conn.cursor()

        query = ('SELECT a.annotation_key, a.annotation_value, a.annotation_desc, sa.timestamp '
                 'FROM system_annotations sa '
                 'LEFT JOIN annotations a ON sa.annotation_id = a.id '
                 'WHERE sa.system_id = %s ')

        try:
            cursor.execute(query, (systemID,))
            result = cursor.fetchall()
        except:
            raise
        finally:
            cursor.close()
            conn.close()

        return result
