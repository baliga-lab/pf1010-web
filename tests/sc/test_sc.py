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
            #print res
            self.assertTrue(res is not None)

    # Ensure that add_comment works correctly
    def test_add_comment(self):
        sc.app.config['SECRET_KEY']=os.urandom(24)
        with sc.app.test_client() as client:
            with client.session_transaction() as sess:
                sess['username']="nisha"
            res=client.post(
                "/add_comment",
                data=dict(newcomment="This is a comment",postid="704b4616-d14e-46a4-ac6e-6d607d86b154")
            )
            #print res
            self.assertTrue(res is not None)

    # Ensure that like_post works correctly
    def test_like_post(self):
        sc.app.config['SECRET_KEY']=os.urandom(24)
        with sc.app.test_client() as client:
            with client.session_transaction() as sess:
                sess['username']="nisha"
            res=client.post(
                "/like_post",
                data=dict(postid="704b4616-d14e-46a4-ac6e-6d607d86b154")
            )
            #print res
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
            print res
            self.assertTrue(res is not None)

    #tests profile page
    def test_profile_page_loads(self):
        with sc.app.test_client() as c:
            response = c.get('/profile')
            self.assertEquals(response.status_code, 200)


    #tests edit profile page
    def test_edit_profile_page_loads(self):
        with sc.app.test_client() as c:
            response = c.get('/editprofile')
            self.assertEquals(response.status_code, 200)

    # End of FlaskTestCase class

    if __name__ == "__main__":
        unittest.main()