#from ... import aqxWeb.sc
import os
import sys
sys.path.append('D:/aqxWeb-NEU/aqxWeb')
from aqxWeb import sc


import unittest


class FlaskTestCase(unittest.TestCase):
    # Ensure that the homepage loads correctly
    def test_home_page_loads(self):
        tester = sc.app.test_client(self)
        response=tester.get("/", content_type="html/text")
        self.assertTrue('Recent Posts',response.data)
    # Ensure that flask was setup correctly
    def test_index(self):
        tester = sc.app.test_client(self)
        response=tester.get("/", content_type="html/text")
        self.assertEqual(response.status_code,200)
    # Ensure that add_post works correctly
    def test_add_post(self):
        sc.app.config['SECRET_KEY']=os.urandom(24)
        with sc.app.test_client() as client:
            with client.session_transaction() as sess:
                sess['username']="nisha"
            res=client.post(
                "/add_post",
                data=dict(privacy="public",text="unittest",link="")
            )
            self.assertTrue(res is not None)
    # Ensure that add_post works correctly
    def test_display_today_post(self):
        sc.app.config['SECRET_KEY']=os.urandom(24)
        with sc.app.test_client() as client:
            with client.session_transaction() as sess:
                sess['username']="nisha"
            res=client.get(
                "/",

            )
            self.assertTrue(res is not None)







    if __name__ == "__main__":
        unittest.main()
