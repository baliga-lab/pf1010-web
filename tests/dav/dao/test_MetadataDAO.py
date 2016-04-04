import unittest
from aqxWeb import run
from aqxWeb.dav import analytics_views
from aqxWeb.dav.dao.MetaDataDAO import MetadataDAO
import MySQLdb
# test DAO for metadata tables

class MetadataDAOTest(unittest.TestCase):

    # Set up method
    def setUp(self):
        self.app = run.app.test_client()
        run.app.config.from_pyfile("system_db.cfg")
        self.conn = MySQLdb.connect(host=run.app.config['HOST'], user=run.app.config['USER'],
                           passwd=run.app.config['PASS'], db=run.app.config['DB'])

    # Tear down method
    def tearDown(self):
        pass

    # get_all_filters
    def test_get_all_filters(self):
        m = MetadataDAO(self.conn)
        response = m.get_all_filters()
        self.assertNotEqual(len(response), 0, 'filters exist')

if __name__ == '__main__':
    unittest.main()