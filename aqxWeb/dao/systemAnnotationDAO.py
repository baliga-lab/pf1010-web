# DAO for system annotation table
from datetime import datetime
import datetime
import MySQLdb

class SystemAnnotationDAO:
    def __init__(self, app):
        self.app = app

    def getDBConn(self):
        return MySQLdb.connect(host=self.app.config['HOST'], user=self.app.config['USER'],
                               passwd=self.app.config['PASS'], db=self.app.config['DB'])

    # add_annotation : adds an annotation to a system
    def add_annotation(self, system_id, annotation_num):
        conn = self.getDBConn()
        old_annotation = self.view_annotation(system_id)
        if len(old_annotation) != 0:
            return "Annotation exists"
        cursor = conn.cursor()

        #annotation_num = 1 mocked data passed

        query = ("insert into system_annotations (system_id,annotation_id,timestamp)    "
                 "values(%s,%s,now()); ")
        data = (system_id, annotation_num)
        try:
            cursor.execute(query, data)
            conn.commit()
        except:
            conn.rollback()
            cursor.close()
            return "Annotation Insert error"
        finally:
            cursor.close()
            conn.close()
        return "Annotation inserted"

    # view_annotation : gets annnotation from a system
    def view_annotation(self, system_id):
        conn = self.getDBConn()
        cursor = conn.cursor()
        query = ('select * from system_annotations where system_id = %s ')
        try:
            cursor.execute(query, (system_id,))
            rows = cursor.fetchall()
        except Exception as ex:
            print "Exception : " + str(ex.message)
        finally:
            cursor.close()
            conn.close()
        return rows