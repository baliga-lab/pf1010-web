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

    #get all measurement types
    def test_get_all_measurement_names(self):
        response = self.app.get('/dav/aqxapi/get/system/measurement_types')
        result = json.loads(response.data)
        self.assertNotEqual(len(result), 0, 'measurements exist')

    #insert user data
    '''def test_put_user(self):
        response=self.app.post('/dav/aqxapi/put/user',
                       data=json.dumps(dict(googleid='98763454054654',
                                            email='test@test.com',
                                            lat=0,
                                            long=0)),
                       content_type = 'application/json')
        result = json.loads(response.data)
        self.assertNotEqual(len(result), 0, 'systems exist')'''


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

    # method to insert test data
    def test_generate_data(self):
        davAPI = DavAPI(self.conn)
        davAPI.generate_data(0,10,
                  ['555d0cfe9ebc11e58153000c29b92d09'],
                  ['o2','ph','temp','alkalinity','ammonium','chlorine','hardness','light','nitrate'])
        self.assertEqual("", "", "Test fail")


     #get the readings for plot
    def test_get_readings_for_plot1(self):
        # data ={}
        # data["system_uid_list"] = ["5cc8402478ee11e59d5c000c29b92d09"]
        # data["measurement_id_list"] = ['8']
        #response = self.app.post('dav/aqxapi/get/readings/time_series_plot',
        #                         data=json.dumps(data), content_type = 'application/json')

        davAPI = DavAPI(self.conn)
        system_uid_list = ["5cc8402478ee11e59d5c000c29b92d09"]
        msr_id_list = ["8"]
        #response = self.app.get('dav/aqxapi/get/readings/tsplot/systems/' + str(system_uid_list) +  '/measurements/' + str(msr_id_list))

        actual_result = davAPI.get_readings_for_plot(system_uid_list,msr_id_list)
        #actual_result = json.loads(response.data)

        expected_result = {"response": [{"system_uid": "5cc8402478ee11e59d5c000c29b92d09", "name": "AQXQA", "measurement": [{"values": [{"y": 105.0, "x": 0, "date": "2016-03-18 18:50:00"}, {"y": 112.0, "x": 1, "date": "2016-03-18 19:45:00"}, {"y": 109.0, "x": 24, "date": "2016-03-19 18:45:00"}], "type": "o2"}]}]}

        #self.assertEqual(len(str(actual_result)),len(str(expected_result)))

    def test_get_readings_for_plot2(self):

        davAPI = DavAPI(self.conn)
        system_uid_list = ["5cc8402478ee11e59d5c000c29b92d09","a26f85668efa11e5997f000c29b92d09"]

        msr_id_list = ["8","5","6"]
        #response = self.app.get('dav/aqxapi/get/readings/tsplot/systems/' + str(system_uid_list) +  '/measurements/' + str(msr_id_list))

        actual_result = davAPI.get_readings_for_plot(system_uid_list,msr_id_list)

        print actual_result

    def test_get_readings_for_plot3(self):

        davAPI = DavAPI(self.conn)
        #system_uid_list =  ["5cc8402478ee11e59d5c000c29b92d09","a26f85668efa11e5997f000c29b92d09","f2dfb67679b811e5a563000c29b92d09","9e08a1ba8efa11e5abff000c29b92d09"]
        system_uid_list =  ["9e08a1ba8efa11e5abff000c29b92d09","5cc8402478ee11e59d5c000c29b92d09"]

        msr_id_list = ["6","8"]
        #response = self.app.get('dav/aqxapi/get/readings/tsplot/systems/' + str(system_uid_list) +  '/measurements/' + str(msr_id_list))

        actual_result = davAPI.get_readings_for_plot(system_uid_list,msr_id_list)

        print actual_result
if __name__ == '__main__':
    unittest.main()
