import unittest
from datetime import datetime

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

    def tearDown(self):
        #u = UserDAO(self.conn)
        #u.delete_user("98763454054654")
        pass

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


    # insert system measurement - current time
    def test_put_system_measurement_new(self):
        time_now = datetime.now()
        print time_now
        response = self.app.post('dav/aqxapi/put/system/measurement',
                                 data=json.dumps(dict(system_uid='555d0cfe9ebc11e58153000c29b92d09',
                                                        measurement_id='5',
                                                        time=str(time_now),
                                                        value='111')),
                                 content_type = 'application/json')
        result = json.loads(response.data)
        status = result['status']
        message = str(status['message'])
        self.assertEqual(message, "Record successfully inserted", "Test fail")

        # insert system measurement - already present time
    def test_put_system_measurement_already_recorded(self):
        response = self.app.post('dav/aqxapi/put/system/measurement',
                                 data=json.dumps(dict(system_uid='555d0cfe9ebc11e58153000c29b92d09',
                                                        measurement_id='5',
                                                        time='2018-03-19 23:28:57',
                                                        value='111')),
                                 content_type = 'application/json')
        result = json.loads(response.data)
        status = result['status']
        message = str(status['message'])
        self.assertEqual(message, "Value at the given time already recorded", "Test fail")

     #get the readings for plot
    def test_get_readings_for_plot(self):
        #davapi = DavAPI()
        #print davapi.get_readings_for_plot(self.conn,[],[])
        data ={}
        data["system_uid_list"] = ["555d0cfe9ebc11e58153000c29b92d09"]
        data["measurement_id_list"] = ['8','9','5']
        response = self.app.post('dav/aqxapi/get/readings/time_series_plot',
                                 data=json.dumps(data), content_type = 'application/json')
        result = json.loads(response.data)

        print result


if __name__ == '__main__':
    unittest.main()
