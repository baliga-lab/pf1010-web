# DAO for system image table
import MySQLdb

class SystemImageDAO:
    def __init__(self, app):
        self.app = app

    def getDBConn(self):
        return MySQLdb.connect(host=self.app.config['HOST'], user=self.app.config['USER'],
                               passwd=self.app.config['PASS'], db=self.app.config['DB'])

    # add_image_to_system: it adds an image to the system_image table
    # id is auto increment
    def add_image_to_system(self, system_id, image):
        conn = self.getDBConn()
        old_image = self.view_image_from_system(image.get('image_id'))
        if len(old_image) != 0:
            return "Image exists"
        cursor = conn.cursor()
        #mocked data for test
        # image = {
        #     'system_id': 111,
        #     'image_url': 'asdfsdaf'
        # }
        query = ("insert into system_images (system_id,image_url)    "
                 "values(%s,%s);")
        data = (image.get('system_id'), image.get('image_url'));
        try:
            cursor.execute(query, data)
            conn.commit()
        except:
            conn.rollback()
            cursor.close()
            return "Insert error"
        finally:
            cursor.close()
            conn.close()
        return "Image inserted"

    #     delete_image_from_system: it delets an image from the system_image table
    def delete_image_from_system(self, system_id, image_id):
        conn = self.getDBConn()
        cursor = conn.cursor()
        query = ("delete from system_images where image_id = %s")
        try:
            cursor.execute(query, (image_id,))
            conn.commit()
        except:
            print "Image del bad"
            conn.rollback()
            cursor.close()
            return "Image delete error"
        finally:
            cursor.close()
            conn.close()
        return "Image deleted"

    # view_image_from_system: it gets an image from the system_image table
    def view_image_from_system(self, system_id, image_id):
        conn = self.getDBConn()
        cursor = conn.cursor()
        query = ('select * from system_images where image_id = %s ')
        try:
            cursor.execute(query, (image_id,))
            system = cursor.fetchall()
        finally:
            cursor.close()
            conn.close()
        return system

    # get a system's all images
    def get_system_all_images(self, system_id):
        conn = self.getDBConn()
        cursor = conn.cursor()
        query = ('select * from system_images where system_id = %s ')

        try:
            cursor.execute(query, (system_id,))
            rows = cursor.fetchall()

        finally:
            cursor.close()
            conn.close()

        return rows