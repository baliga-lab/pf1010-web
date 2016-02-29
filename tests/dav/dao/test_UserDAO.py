import unittest
from aqxWeb import run
from aqxWeb.dav import analyticsViews
from aqxWeb.dav.dao.UserDAO import UserDAO
import json

# test DAO for users table


class UserDAOTest(unittest.TestCase):

    def setUp(self):
        self.app = run.app.test_client()
        analyticsViews.init_app(run.app)
        self.conn = analyticsViews.get_conn()

    def tearDown(self):
        u = UserDAO(self.conn)
        u.delete_user("6546546465")
        pass

    #get user data
    def test_get_user(self):
        u = UserDAO(self.conn)
        response = u.get_user("108935443071440000056")
        self.assertNotEqual(len(response), 0, 'user exist')

    #insert user data
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
