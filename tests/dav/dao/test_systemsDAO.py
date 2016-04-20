import unittest
from aqxWeb import run
from aqxWeb.dav import analytics_views
from aqxWeb.dav.dao.systemsDAO import SystemsDAO
import MySQLdb
# test DAO for systems table


class SystemsDAOTest(unittest.TestCase):

    def setUp(self):
        run.app.config.from_pyfile("system_db.cfg")
        self.app = run.app

    def tearDown(self):
        pass

    # get all system data
    def test_get_all_systems_info(self):
        s = SystemsDAO(self.app)
        response = s.get_all_systems_info()
        self.assertNotEqual(len(response), 0, 'systems exist')


if __name__ == '__main__':
    unittest.main()
