import unittest
from aqxWeb import run
from aqxWeb.dav import analyticsViews
from aqxWeb.dav.dao.MeasurementsDAO import MeasurementsDAO

# test DAO for metadata tables

class MeasurementsDAOTest(unittest.TestCase):

    # Set up method
    def setUp(self):
        self.app = run.app.test_client()
        analyticsViews.init_app(run.app)
        self.conn = analyticsViews.get_conn()

    # Tear down method
    def tearDown(self):
        pass

    # get_all_measurements
    def test_get_measurements(self):
        m = MeasurementsDAO(self.conn)
        response = m.get_measurements(["555d0cfe9ebc11e58153000c29b92d09"],["o2","ph","light"])
        print response
        print response['555d0cfe9ebc11e58153000c29b92d09']['o2']
        self.assertNotEqual(len(response), 0, 'filters exist')

if __name__ == '__main__':
    unittest.main()