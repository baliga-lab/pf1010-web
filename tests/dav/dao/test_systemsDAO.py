import unittest
from aqxWeb import run
from aqxWeb.dav import analytics_views
from aqxWeb.dav.dao.systemsDAO import SystemsDAO
import MySQLdb
# test DAO for systems table


class SystemsDAOTest(unittest.TestCase):

    def setUp(self):
        self.app = run.app.test_client()
        run.app.config.from_pyfile("system_db.cfg")
        self.conn = MySQLdb.connect(host=run.app.config['HOST'], user=run.app.config['USER'],
                           passwd=run.app.config['PASS'], db=run.app.config['DB'])

    def tearDown(self):
        pass

    # get all system data
    def test_get_all_systems_info(self):
        s = SystemsDAO(self.conn)
        response = s.get_all_systems_info()
        self.assertNotEqual(len(response), 0, 'systems exist')


if __name__ == '__main__':
    unittest.main()
