# DAO for system annotation table
from datetime import datetime
import datetime

class SystemAnnotationDAO:
    def __init__(self, conn):
        self.conn = conn

    # add_annotation : adds an annotation to a system
    def add_annotation(self, system_id, annotation_num):
        old_annotation = self.view_annotation(system_id)
        if len(old_annotation) != 0:
            return "Annotation exists"
        cursor = self.conn.cursor()

        #annotation_num = 1 mocked data passed

        query = ("insert into system_annotations (system_id,annotation_id,timestamp)    "
                 "values(%s,%s,now()); ")
        data = (system_id, annotation_num)
        try:
            cursor.execute(query, data)
            self.conn.commit()
        except:
            self.conn.rollback()
            cursor.close()
            return "Annotation Insert error"
        finally:
            cursor.close()
        return "Annotation inserted"

    # view_annotation : gets an nnotation from a system
    def view_annotation(self, system_id):
        cursor = self.conn.cursor()
        query = ('select * from system_annotations where system_id = %s ')
        try:
            cursor.execute(query, (system_id,))
            system = cursor.fetchall()
        finally:
            cursor.close()
        return system