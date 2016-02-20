import unittest
from aqxWeb import app
import json
from aqxWeb.dav.dao.UserDAO import UserDAO

# test DAV Api calls


class DavApiTest(unittest.TestCase):
    def setUp(self):
        self.app = app.app.test_client()
        app.init_app(self.app)
        self.conn = app.get_conn()

    def tearDown(self):
        u = UserDAO(self.conn)
        u.delete_user("98763454054654")
        pass

    #get all systems
    def test_get_all_systems_info(self):
        response = self.app.get('/aqxapi/get/systems/metadata')
        print(response)
        result = json.loads(response.data)
        self.assertNotEqual(len(result), 0, 'systems exist')

    #insert user data
    def test_put_user(self):
        response=self.app.post('/aqxapi/put/user',
                       data=json.dumps(dict(googleid='98763454054654',
                                            email='test@test.com',
                                            lat=0,
                                            long=0)),
                       content_type = 'application/json')
        result = json.loads(response.data)
        self.assertNotEqual(len(result), 0, 'systems exist')


if __name__ == '__main__':
    unittest.main()
