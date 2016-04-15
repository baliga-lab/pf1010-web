# DAO for system image table

class SystemImageDAO:
    def __init__(self, conn):
        self.conn = conn

    # add_image_to_system: it adds an image to the system_image table
    # id is auto increment
    def add_image_to_system(self, system_id, image):
        old_image = self.view_image_from_system(image.get('image_id'))
        if len(old_image) != 0:
            return "Image exists"
        cursor = self.conn.cursor()
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
            self.conn.commit()
        except:
            self.conn.rollback()
            cursor.close()
            return "Insert error"
        finally:
            cursor.close()
        return "Image inserted"

    #     delete_image_from_system: it delets an image from the system_image table
    def delete_image_from_system(self, system_id, image_id):
        cursor = self.conn.cursor()
        query = ("delete from system_images where image_id = %s")
        try:
            cursor.execute(query, (image_id,))
            self.conn.commit()
        except:
            print "Image del bad"
            self.conn.rollback()
            cursor.close()
            return "Image delete error"
        finally:
            cursor.close()
        return "Image deleted"

    # view_image_from_system: it gets an image from the system_image table
    def view_image_from_system(self, system_id, image_id):
        cursor = self.conn.cursor()
        query = ('select * from system_images where image_id = %s ')
        try:
            cursor.execute(query, (image_id,))
            system = cursor.fetchall()
        finally:
            cursor.close()
        return system

    # get a system's all images
    def get_system_all_images(self, system_id):
        cursor = self.conn.cursor()
        query = ('select * from system_images where system_id = %s ')

        try:
            cursor.execute(query, (system_id,))
            rows = cursor.fetchall()

        finally:
            cursor.close()
            self.conn.close()

        return rows