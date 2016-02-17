import unittest
from aqxWeb import app
from aqxWeb.dav.dao.UserDAO import UserDAO
import json


class UserDAOTest(unittest.TestCase):

    def setUp(self):
        self.app = app.app.test_client()
        app.init_app(self.app)
        self.conn = app.get_conn()

    def tearDown(self):
        u = UserDAO(self.conn)
        u.delete_user("6546546465")
        pass

    def test_get_user(self):
        u = UserDAO(self.conn)
        response = u.get_user("108935443071440000056")
        self.assertNotEqual(len(response), 0, 'user exist')

    def test_put_user(self):
        user = {"googleid" : "6546546465",
                "email" : "asdasd@as.com",
                "lat" : 0,
                "long" : 0}
        u = UserDAO(self.conn)
        response = u.put_user(user)
        self.assertEqual(response, "User inserted", "User inserted")


if __name__ == '__main__':
    unittest.main()
