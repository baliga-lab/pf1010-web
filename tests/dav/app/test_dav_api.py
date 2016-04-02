import unittest
from datetime import datetime

from aqxWeb import run
from aqxWeb.dav import analytics_views
from aqxWeb.dav.app.dav_api import DavAPI

import json
import MySQLdb
# test DAV Api calls


class DavApiTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = run.app.test_client()
        run.app.config.from_pyfile("system_db.cfg")
        run.create_conn(run.app)
        run.init_dav(run.pool)
        cls.conn = MySQLdb.connect(host=run.app.config['HOST'], user=run.app.config['USER'],
                                   passwd=run.app.config['PASS'], db=run.app.config['DB'])

        # cls.conn = MySQLdb.connect(host=run.app.config['HOST'], user=run.app.config['USER'],
        #                   passwd=run.app.config['PASS'], db=run.app.config['DB'])

    def tearDown(self):
        pass

    # get all systems
    def test_get_all_systems_info(self):
        response = self.app.get('/dav/aqxapi/get/systems/metadata')
        print(response)
        result = json.loads(response.data)
        self.assertNotEqual(len(result), 0, 'systems exist')

    # get all measurement types
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
                                 content_type='application/json')
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
                                 content_type='application/json')
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
    # 1  data present for O2 for "5cc8402478ee11e59d5c000c29b92d09"

    def test_get_readings_for_plot1(self):
        davAPI = DavAPI(self.conn)
        system_uid_list = ["5cc8402478ee11e59d5c000c29b92d09"]
        msr_id_list = ["8"]
        actual_result = davAPI.get_readings_for_plot(system_uid_list, msr_id_list, 200)
        with open('data/test_get_readings_for_plot1_er.txt') as f:
            expected_result = f.readlines()[0]
        self.assertEqual(expected_result, actual_result)

    # 2  data present for nitrate,O2,pH for "5cc8402478ee11e59d5c000c29b92d09"

    def test_get_readings_for_plot2(self):
        davAPI = DavAPI(self.conn)
        system_uid_list = ["5cc8402478ee11e59d5c000c29b92d09"]

        msr_id_list = ["6", "8", "9"]

        actual_result = davAPI.get_readings_for_plot(system_uid_list, msr_id_list, 200)

        with open('data/test_get_readings_for_plot2_er.txt') as f:
            expected_result = f.readlines()[0]
        print actual_result
        self.assertEqual(expected_result, actual_result)

    # 3  data present for nitrate for "555d0cfe9ebc11e58153000c29b92d09","5cc8402478ee11e59d5c000c29b92d09","6b62eb76451211e5a1d4000c29b92d09"

    def test_get_readings_for_plot3(self):
        system_uid_list = ["555d0cfe9ebc11e58153000c29b92d09", "5cc8402478ee11e59d5c000c29b92d09",
                           "6b62eb76451211e5a1d4000c29b92d09"]
        msr_id_list = [6]

        actual_result = analytics_views.get_readings_for_tsplot(system_uid_list, msr_id_list)
        with open('data/test_get_readings_for_plot3_er.txt') as f:
            expected_result = f.readlines()[0]
        print actual_result

        self.assertEqual(expected_result, actual_result)

    # 4 data present for nitrate,O2,pH for "555d0cfe9ebc11e58153000c29b92d09","5cc8402478ee11e59d5c000c29b92d09","6b62eb76451211e5a1d4000c29b92d09"

    def test_get_readings_for_plot4(self):
        system_uid_list = ["555d0cfe9ebc11e58153000c29b92d09", "5cc8402478ee11e59d5c000c29b92d09",
                           "6b62eb76451211e5a1d4000c29b92d09"]
        msr_id_list = [6, 8, 9]

        actual_result = analytics_views.get_readings_for_tsplot(system_uid_list, msr_id_list, 400)
        with open('data/test_get_readings_for_plot4_er.txt') as f:
            expected_result = f.readlines()[0]

        self.assertEqual(expected_result, actual_result)

    # Tests 2 systems with 2 measurement ids.
    # SYSTEM1: b9752004864911e58f3f000c29b92d09
    # SYSTEM2: 3ddb948a5afe11e5a2ac000c29b92d09
    # MEASUREMENT1: alkalinity (SYSTEM1)
    # MEASUREMENT2: chlorine (SYSTEM1)
    # MEASUREMENT3: hardness(SYSTEM1)
    def test_get_readings_for_plot5(self):
        system_uid_list = ["b9752004864911e58f3f000c29b92d09", "3ddb948a5afe11e5a2ac000c29b92d09"]
        msr_id_list = ["1", "3", "4"]
        actual_result = analytics_views.get_readings_for_tsplot(system_uid_list, msr_id_list)
        with open('data/test_get_readings_for_plot5_er.txt') as f:
            expected_result = f.readlines()[0]

        self.assertEqual(expected_result, actual_result)

    # Tests 2 systems with 4 measurement ids.
    # SYSTEM1: 3ddb948a5afe11e5a2ac000c29b92d09
    # SYSTEM2: b9cf213a8efa11e587db000c29b92d09
    # MEASUREMENT1: alkalinity (SYSTEM2)
    # MEASUREMENT3: light(SYSTEM1)
    def test_get_readings_for_plot6(self):
        system_uid_list = ["3ddb948a5afe11e5a2ac000c29b92d09", "b9cf213a8efa11e587db000c29b92d09"]
        msr_id_list = [1, 5]
        actual_result = analytics_views.get_readings_for_tsplot(system_uid_list, msr_id_list)
        print actual_result
        with open('data/test_get_readings_for_plot6_er.txt') as f:
            expected_result = f.readlines()[0]

        self.assertEqual(expected_result, actual_result)

    def test_get_readings_for_plot7(self):
        system_uid_list = ["cb08e32e41f111e5b93f000c29b92d09", "8fb1f712bf1d11e5adcc000c29b92d09"]
        msr_id_list = [6, 8, 9]

        actual_result = analytics_views.get_readings_for_tsplot(system_uid_list, msr_id_list)
        print actual_result
        with open('data/test_get_readings_for_plot7_er.txt') as f:
            expected_result = f.readlines()[0]

        self.assertEqual(expected_result, actual_result)

    def test_get_readings_for_phases_plot1(self):
        system_uid_list = ["eecce02681bb11e5904b000c29b92d09"]
        msr_id_list = [8]
        status_id = 400
        actual_result = analytics_views.get_readings_for_tsplot(system_uid_list, msr_id_list, status_id)
        print actual_result

    def test_get_readings_for_phases_plot2(self):
        system_uid_list = ["eecce02681bb11e5904b000c29b92d09", "555d0cfe9ebc11e58153000c29b92d09"]
        msr_id_list = [8]
        status_id = 200
        actual_result = analytics_views.get_readings_for_tsplot(system_uid_list, msr_id_list, status_id)
        print actual_result

    def test_get_readings_for_phases_plot3(self):
        system_uid_list = ["eecce02681bb11e5904b000c29b92d09", "555d0cfe9ebc11e58153000c29b92d09"]
        msr_id_list = [6, 8]
        status_id = 200
        actual_result = analytics_views.get_readings_for_tsplot(system_uid_list, msr_id_list, status_id)
        print actual_result

    # negative test case, querying non existent table

    def test_get_readings_for_plot2_neg(self):
        davAPI = DavAPI(self.conn)
        system_uid_list = ["5cc840478ee11e59d5c000c29b92d09"]
        msr_id_list = ["6"]
        actual_result = davAPI.get_readings_for_plot(system_uid_list, msr_id_list)
        print actual_result
        self.assertTrue("error" in actual_result)

    # test for get_readings_for_plot
    def test_get_readings_for_plot(self):
        system_uid_list = ["5cc8402478ee11e59d5c000c29b92d09"]
        msr_id_list = ["8"]
        status_id = 100
        response = self.app.post('dav/aqxapi/v1/measurements/plot',
                                 data=json.dumps(dict(systems=system_uid_list,
                                                      measurements=msr_id_list,
                                                      status=status_id)),
                                 content_type='application/json')
        actual_status_code = response._status_code
        expected_status_code = 200
        actual_result_temp = json.loads(response.data)
        actual_result = json.dumps(actual_result_temp)
        with open('data/test_get_readings_for_plot.txt') as f:
            expected_result = f.readlines()[0]
        self.assertEqual(expected_result, actual_result)
        self.assertEquals(expected_status_code, actual_status_code)

    # test for get_system_measurements (for system_uid = 555d0cfe9ebc11e58153000c29b92d09)
    def test_get_system_measurements(self):
        response = self.app.get('/dav/aqxapi/v1/measurements?system_uid=555d0cfe9ebc11e58153000c29b92d09')
        actual_status_code = response._status_code
        expected_status_code = 200
        actual_result_temp = json.loads(response.data)
        actual_result = json.dumps(actual_result_temp)
        with open('data/test_get_system_measurements.txt') as f:
            expected_result = f.readlines()[0]
        self.assertEquals(expected_result, actual_result)
        self.assertEquals(expected_status_code, actual_status_code)

    # test for get_system_measurements (for system_uid = null)
    def test_get_system_measurements_with_null_system_uid(self):
        response = self.app.get('/dav/aqxapi/v1/measurements?system_uid=null')
        actual_status_code = response._status_code
        expected_status_code = 400
        actual_result_temp = json.loads(response.data)
        actual_result = json.dumps(actual_result_temp)
        expected_result = '{"error": "Table \'projectfeed.aqxs_alkalinity_null\' doesn\'t exist"}'
        self.assertEquals(expected_result, actual_result)
        self.assertEquals(expected_status_code, actual_status_code)

    # test for get_system_measurements (for url parameter for system_uid is not given)
    def test_get_system_measurements_with_no_system_uid(self):
        response = self.app.get('/dav/aqxapi/v1/measurements?system_uid=')
        actual_status_code = response._status_code
        expected_status_code = 400
        actual_result_temp = json.loads(response.data)
        actual_result = json.dumps(actual_result_temp)
        expected_result = '{"error": "Invalid system_uid"}'
        self.assertEquals(expected_result, actual_result)
        self.assertEquals(expected_status_code, actual_status_code)

    # test for get_system_measurement ( for system_uid = 555d0cfe9ebc11e58153000c29b92d09,
    # measurement_id = 1, both system_uid and measurement_id is valid in this case)
    def test_get_system_measurement_1(self):
        response = self.app.get(
            '/dav/aqxapi/v1/measurements?system_uid=555d0cfe9ebc11e58153000c29b92d09&measurement_id=1')
        actual_status_code = response._status_code
        expected_status_code = 200
        actual_result_temp = json.loads(response.data)
        actual_result = json.dumps(actual_result_temp)
        with open('data/test_get_system_measurement_1.txt') as f:
            expected_result = f.readlines()[0]
        self.assertEquals(expected_result, actual_result)
        self.assertEquals(expected_status_code, actual_status_code)

    # test for get_system_measurement ( for system_uid is not given,
    # measurement_id = 1)
    def test_get_system_measurement_2(self):
        response = self.app.get(
            '/dav/aqxapi/v1/measurements?system_uid=&measurement_id=1')
        actual_status_code = response._status_code
        expected_status_code = 400
        actual_result_temp = json.loads(response.data)
        actual_result = json.dumps(actual_result_temp)
        expected_result = '{"error": "Invalid system_uid"}'
        self.assertEquals(expected_result, actual_result)
        self.assertEquals(expected_status_code, actual_status_code)

    # test for get_system_measurement ( for system_uid = 555d0cfe9ebc11e58153000c29b92d09,
    # measurement_id is not given. system_uid is valid and measurement_id is invalid)
    def test_get_system_measurement_3(self):
        response = self.app.get(
            '/dav/aqxapi/v1/measurements?system_uid=555d0cfe9ebc11e58153000c29b92d09&measurement_id=')
        actual_status_code = response._status_code
        expected_status_code = 400
        actual_result_temp = json.loads(response.data)
        actual_result = json.dumps(actual_result_temp)
        expected_result = '{"error": "Invalid measurement id"}'
        self.assertEquals(expected_result, actual_result)
        self.assertEquals(expected_status_code, actual_status_code)

    # test for get_system_measurement ( for system_uid = 555d0cfe9ebc11e58153000c29b92d09,
    # measurement_id = 100. system_uid is valid and measurement_id is invalid)
    def test_get_system_measurement_4(self):
        response = self.app.get(
            '/dav/aqxapi/v1/measurements?system_uid=555d0cfe9ebc11e58153000c29b92d09&measurement_id=100')
        actual_status_code = response._status_code
        expected_status_code = 400
        actual_result_temp = json.loads(response.data)
        actual_result = json.dumps(actual_result_temp)
        expected_result = '{"error": "Invalid measurement id"}'
        self.assertEquals(expected_result, actual_result)
        self.assertEquals(expected_status_code, actual_status_code)

    # test for get_system_measurement ( for system_uid = 555d0cfe9ebc11e58153000c29b92d09,
    # measurement_id = 5, both system_uid and measurement_id is valid in this case)
    # As measurement_id = 5 (light), latest 7 records are returned
    def test_get_system_measurement_5(self):
        response = self.app.get(
            '/dav/aqxapi/v1/measurements?system_uid=555d0cfe9ebc11e58153000c29b92d09&measurement_id=5')
        actual_status_code = response._status_code
        expected_status_code = 200
        actual_result_temp = json.loads(response.data)
        actual_result = json.dumps(actual_result_temp)
        with open('data/test_get_system_measurement_5.txt') as f:
            expected_result = f.readlines()[0]
        self.assertEquals(expected_result, actual_result)
        self.assertEquals(expected_status_code, actual_status_code)


if __name__ == '__main__':
    unittest.main()
