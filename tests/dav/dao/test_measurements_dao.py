import unittest
from aqxWeb import run
import MySQLdb
from aqxWeb.dav.dao.measurements_dao import MeasurementsDAO
import os

# test DAO for metadata tables

class MeasurementsDAOTest(unittest.TestCase):

    # Set up method
    def setUp(self):
        run.app.config.from_pyfile("system_db.cfg")
        self.app = run.app

    # Tear down method
    def tearDown(self):
        pass

    # get_all_measurements
    def test_get_measurements(self):
        m = MeasurementsDAO(self.app)
        response = m.get_measurements(["555d0cfe9ebc11e58153000c29b92d09"],["o2","ph","light"],200)
        print response
        print response['555d0cfe9ebc11e58153000c29b92d09']['o2']
        test = response['555d0cfe9ebc11e58153000c29b92d09']
        print test['ph']
        self.assertNotEqual(len(response), 0, 'filters exist')

    # get_all_measurements
    def test_get_all_measurement_names(self):
        m = MeasurementsDAO(self.app)
        response = m.get_all_measurement_names()
        print response
        self.assertNotEqual(len(response), 0, 'measurements exist')

    def test_get_time_ranges_for_status(self):
        m = MeasurementsDAO(self.app)
        response = m.get_time_ranges_for_status('eecce02681bb11e5904b000c29b92d09',100)

    def test_get_status_type(self):
        m = MeasurementsDAO(self.app)
        response = m.get_status_type(200)
        print response
        self.assertEqual('established',response)

    def test_get_annotations(self):
        m = MeasurementsDAO(self.app)
        systems = ["ad0ecd9c8efa11e5997f000c29b92d09","41c154185afe11e59fd1000c29b92d09"]
        response = m.get_annotations(systems)
        print response

if __name__ == '__main__':
    unittest.main()