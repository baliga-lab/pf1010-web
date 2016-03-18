from mock import Mock
import unittest
from aqxWeb.dav.app.davAPI import DavAPI

class dav_tests(unittest.TestCase):

    def test_get_system_measurement(self):
        d = DavAPI(Mock())
        d.mea = Mock()
        result = ((321321,10),(321321,10))
        a = tuple(("light",))
        d.mea.get_latest_value.return_value = tuple(result)
        d.mea.get_measurement_name.return_value = tuple(("light",))
        result = d.get_system_measurement('555d0cfe9ebc11e58153000c29b92d09','9')
        self.assertEquals('{"records": [{"value": "10", "time": "321321"}, {"value": "10", "time": "321321"}], "system_uid": "555d0cfe9ebc11e58153000c29b92d09"}', result)