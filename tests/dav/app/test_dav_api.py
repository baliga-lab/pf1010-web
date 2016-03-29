import unittest
from datetime import datetime

from aqxWeb import run
from aqxWeb.dav import analytics_views
from aqxWeb.dav.app.dav_api import DavAPI

import json

# test DAV Api calls


class DavApiTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = run.app.test_client()
        analytics_views.init_app(run.app)
        cls.conn = analytics_views.get_conn()

    def tearDown(self):
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
        self.assertEqual(message, "Value at the given time already recorded", "Test pass")

    # method to insert test data
    # def test_generate_data(self):
    #     davAPI = DavAPI(self.conn)
    #     davAPI.generate_data(0,10,
    #               ['5cc8402478ee11e59d5c000c29b92d09'],
    #              # ['o2','ph','temp','alkalinity','ammonium','chlorine','hardness','light','nitrate'])
    #                          ['light'])
    #     self.assertEqual("", "", "Test fail")


    ###  get the readings for plot TESTCASES
    #1  data present for O2 for "5cc8402478ee11e59d5c000c29b92d09"

    def test_get_readings_for_plot1(self):

        davAPI = DavAPI(self.conn)
        system_uid_list = ["5cc8402478ee11e59d5c000c29b92d09"]
        msr_id_list = ["8"]
        actual_result = davAPI.get_readings_for_plot(system_uid_list,msr_id_list)
        with open('data/test_get_readings_for_plot1_er.txt') as f:
            expected_result = f.readlines()[0]
        self.assertEqual(expected_result,actual_result)

    #2  data present for nitrate,O2,pH for "5cc8402478ee11e59d5c000c29b92d09"

    def test_get_readings_for_plot2(self):

        davAPI = DavAPI(self.conn)
        system_uid_list = ["5cc8402478ee11e59d5c000c29b92d09"]

        msr_id_list = ["6","8","9"]

        actual_result = davAPI.get_readings_for_plot(system_uid_list,msr_id_list)

        with open('data/test_get_readings_for_plot2_er.txt') as f:
            expected_result = f.readlines()[0]
        print actual_result
        self.assertEqual(expected_result,actual_result)

    #3  data present for nitrate for "555d0cfe9ebc11e58153000c29b92d09","5cc8402478ee11e59d5c000c29b92d09","6b62eb76451211e5a1d4000c29b92d09"

    def test_get_readings_for_plot3(self):

        system_uid_list =  ["555d0cfe9ebc11e58153000c29b92d09","5cc8402478ee11e59d5c000c29b92d09","6b62eb76451211e5a1d4000c29b92d09"]
        msr_id_list = [6]

        actual_result =   analytics_views.get_readings_for_tsplot(system_uid_list, msr_id_list)
        with open('data/test_get_readings_for_plot3_er.txt') as f:
            expected_result = f.readlines()[0]
        print actual_result

        self.assertEqual(expected_result,actual_result)

    #4 data present for nitrate,O2,pH for "555d0cfe9ebc11e58153000c29b92d09","5cc8402478ee11e59d5c000c29b92d09","6b62eb76451211e5a1d4000c29b92d09"

    def test_get_readings_for_plot4(self):

        system_uid_list =  ["555d0cfe9ebc11e58153000c29b92d09","5cc8402478ee11e59d5c000c29b92d09","6b62eb76451211e5a1d4000c29b92d09"]
        msr_id_list = [6,8,9]

        actual_result =   analytics_views.get_readings_for_tsplot(system_uid_list, msr_id_list)
        with open('data/test_get_readings_for_plot4_er.txt') as f:
            expected_result = f.readlines()[0]

        self.assertEqual(expected_result,actual_result)

    # Tests 2 systems with 2 measurement ids.
    # SYSTEM1: b9752004864911e58f3f000c29b92d09
    # SYSTEM2: 3ddb948a5afe11e5a2ac000c29b92d09
    # MEASUREMENT1: alkalinity (SYSTEM1)
    # MEASUREMENT2: chlorine (SYSTEM1)
    # MEASUREMENT3: hardness(SYSTEM1)
    def test_get_readings_for_plot5(self):
        system_uid_list = ["b9752004864911e58f3f000c29b92d09","3ddb948a5afe11e5a2ac000c29b92d09"]
        msr_id_list = ["1", "3", "4"]
        actual_result = analytics_views.get_readings_for_tsplot(system_uid_list, msr_id_list)
        with open('data/test_get_readings_for_plot5_er.txt') as f:
            expected_result = f.readlines()[0]

        self.assertEqual(expected_result,actual_result)

    # Tests 2 systems with 4 measurement ids.
    # SYSTEM1: 3ddb948a5afe11e5a2ac000c29b92d09
    # SYSTEM2: b9cf213a8efa11e587db000c29b92d09
    # MEASUREMENT1: alkalinity (SYSTEM2)
    # MEASUREMENT3: light(SYSTEM1)
    def test_get_readings_for_plot6(self):
        system_uid_list = ["3ddb948a5afe11e5a2ac000c29b92d09","b9cf213a8efa11e587db000c29b92d09"]
        msr_id_list = [1, 5]
        actual_result = analytics_views.get_readings_for_tsplot(system_uid_list, msr_id_list)
        print actual_result
        with open('data/test_get_readings_for_plot6_er.txt') as f:
            expected_result = f.readlines()[0]

        self.assertEqual(expected_result,actual_result)


    def test_get_readings_for_plot7(self):

        system_uid_list =  ["cb08e32e41f111e5b93f000c29b92d09","8fb1f712bf1d11e5adcc000c29b92d09"]
        msr_id_list = [6,8,9]

        actual_result =   analytics_views.get_readings_for_tsplot(system_uid_list, msr_id_list)
        print actual_result
        with open('data/test_get_readings_for_plot7_er.txt') as f:
            expected_result = f.readlines()[0]

        self.assertEqual(expected_result,actual_result)


    #negative test case, querying non existent table

    def test_get_readings_for_plot2_neg(self):

        davAPI = DavAPI(self.conn)
        system_uid_list = ["5cc840478ee11e59d5c000c29b92d09"]
        msr_id_list = ["6"]
        actual_result = davAPI.get_readings_for_plot(system_uid_list,msr_id_list)
        print actual_result
        self.assertTrue("error" in actual_result)

if __name__ == '__main__':
    unittest.main()
