from mock import Mock
import unittest
from aqxWeb.dav.app.davAPI import DavAPI


class DavTests(unittest.TestCase):

    #mock method for get_system_measurement

    def test_get_system_measurement(self):
        d = DavAPI(Mock())
        d.mea = Mock()
        result = ((321321,10),(321321,10))
        a = tuple(("light",))
        d.mea.get_latest_value.return_value = tuple(result)
        d.mea.get_measurement_name.return_value = tuple(("light",))
        result = d.get_system_measurement('555d0cfe9ebc11e58153000c29b92d09','9')
        self.assertEquals('{"records": [{"value": "10", "time": "321321"}, {"value": "10", "time": "321321"}], "system_uid": "555d0cfe9ebc11e58153000c29b92d09"}', result)


    #mock method for get_system_measurement

    def test_get_all_measurement_names(self):
        d = DavAPI(Mock())
        d.mea = Mock()
        result = (u'o2', u'ph', u'temp', u'alkalinity', u'ammonium', u'chlorine', u'hardness', u'light', u'nitrate', 'time')
        d.mea.get_all_measurement_names.return_value = tuple(result)
        result = d.get_all_measurement_names()
        self.assertEquals('{"types": ["o2", "ph", "temp", "alkalinity", "ammonium", "chlorine", "hardness", "light", "nitrate", "time", "time"]}', result)
