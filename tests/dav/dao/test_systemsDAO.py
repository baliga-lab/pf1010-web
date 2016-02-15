import unittest
from aqxWeb import app
import json

# test DAO for systems table


class SystemsDAOTest(unittest.TestCase):
    def setUp(self):
        self.app = app.app.test_client()
        app.init_app(self.app)

    def tearDown(self):
        pass

    def test_get_systems(self):
        response = self.app.get('/aqxapi/get/systems')
        print(response)
        result = json.loads(response.data)
        self.assertNotEqual(len(result), 0, 'systems exist')


if __name__ == '__main__':
    unittest.main()
