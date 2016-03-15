import unittest
from aqxWeb import run
from aqxWeb.dav import analyticsViews
from aqxWeb.dav.app.davAPI import DavAPI

import json
from aqxWeb.dav.dao.UserDAO import UserDAO

# test DAV Api calls


class DavApiTest(unittest.TestCase):
    def setUp(self):
        self.app = run.app.test_client()
        analyticsViews.init_app(run.app)
        self.conn = analyticsViews.get_conn()

    # def tearDown(self):
    #     u = UserDAO(self.conn)
    #     u.delete_user("98763454054654")
    #     pass

    #get all systems
    def test_get_all_systems_info(self):
        response = self.app.get('/dav/aqxapi/get/systems/metadata')
        print(response)
        result = json.loads(response.data)
        self.assertNotEqual(len(result), 0, 'systems exist')

    #insert user data
    def test_put_user(self):
        response=self.app.post('/dav/aqxapi/put/user',
                       data=json.dumps(dict(googleid='98763454054654',
                                            email='test@test.com',
                                            lat=0,
                                            long=0)),
                       content_type = 'application/json')
        result = json.loads(response.data)
        self.assertNotEqual(len(result), 0, 'systems exist')

    #get the readings for plot
    def test_get_readings_for_plot(self):
        davapi = DavAPI()
        print davapi.get_readings_for_plot(self.conn,[],[])


if __name__ == '__main__':
    unittest.main()
