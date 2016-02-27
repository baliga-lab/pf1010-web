import unittest
from aqxWeb import app
from aqxWeb.dav.dao.systemsDAO import SystemsDAO

# test DAO for systems table


class SystemsDAOTest(unittest.TestCase):
    def setUp(self):
        self.app = app.app.test_client()
        app.init_app(self.app)
        self.conn = app.get_conn()

    def tearDown(self):
        pass

    #get all system data
    def test_get_all_systems_info(self):
        s = SystemsDAO(self.conn)
        response = s.get_all_systems_info()
        self.assertNotEqual(len(response), 0, 'systems exist')


if __name__ == '__main__':
    unittest.main()
