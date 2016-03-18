import os
import unittest
from flask import Flask, url_for
from aqxWeb.sc.models import init_sc_app
from aqxWeb.sc.views import social

app = Flask(__name__)
app.config.from_pyfile("../../aqxWeb/sc/settings.cfg")
app.secret_key = os.urandom(24)
app.register_blueprint(social, url_prefix='/social')
init_sc_app(app)


class FlaskTestCase(unittest.TestCase):
    # Ensure that the homepage loads correctly
    def test_home_page_loads(self):
        tester = app.test_client(self)
        response = tester.get("/", content_type="html/text")
        self.assertTrue('Recent Posts', response.data)

    # Ensure that flask was setup correctly
    def test_index(self):
        tester = app.test_client(self)
        response = tester.get("/", content_type="html/text")
        self.assertTrue(response.status_code, response.data)

    # Ensure that add_post works correctly
    def test_add_post(self):
        with app.test_client() as client:
            with client.session_transaction() as sess:
                sess['username'] = "nisha"
            res = client.post(
                "/test_add_post",
                data=dict(privacy="public", text="unittest", link="")
            )
            self.assertTrue(res is not None)

    # Ensure that add_comment works correctly
    def test_add_comment(self):
        with app.test_client() as client:
            with client.session_transaction() as sess:
                sess['username'] = "nisha"
            res = client.post(
                "/add_comment",
                data=dict(newcomment="This is a comment", postid="1")
            )
            self.assertTrue(res is not None)

    # Ensure that like_post works correctly
    def test_like_post(self):
        with app.test_client() as client:
            with client.session_transaction() as sess:
                sess['username'] = "nisha"
            res = client.post(
                "/like_post",
                data=dict(postid="1")
            )
            self.assertTrue(res is not None)

    # Ensure that add_post works correctly
    def test_display_today_post(self):
        with app.test_client() as client:
            with client.session_transaction() as sess:
                sess['username'] = "nisha"
            res = client.get(
                "/",

            )
            self.assertTrue(res is not None)

    # Ensure that test_add_user works correctly
    def test_add_user(self):
        with app.test_client() as client:
            res = client.post(
                "/testSignin",
                data=dict(givenName="test", familyName="123", email="test123@gmail.com", id="test123")
            )
            self.assertTrue(res.status_code, 200)

            # tests edit profile page

    def test_edit_profile_page_loads(self):
        with app.test_client() as client:
            response = client.get('/social/editprofile')
            # Negative Testing
            self.assert_("Gender" not in response.data, "Guest user should not be able to access the edit profile page")
            with client.session_transaction() as session:
                session['uid'] = 999
            response = client.get('/social/editprofile')
            # Positive Testing
            self.assertEquals(response.status_code, 200,
                              "Logged In User should be able to access the edit profile page")
            self.assert_("gender" in response.data, "Logged In User should be able to view his/her gender information")

    def test_search_systems(self):
        with app.test_client() as client:
            response = client.get('/social/systems')
            # Page Load Negative Testing
            self.assert_("Gender" not in response.data, "Guest user will not be able to access the search systems page")
            with client.session_transaction() as session:
                session['uid'] = 999
            response = client.get('/social/systems')
            # Page Load Positive Testing
            self.assertEquals(response.status_code, 200,
                              "Logged In User should be able to access the search systems page")
            self.assert_("Participated" in response.data,
                         "Logged In User should be able to view the systems he/she participated on")
            # Search For System With System Name As Parameter
            searchParam = "&^$%"
            response = client.post(
                "/social/systems",
                data=dict(txtSystemName=searchParam)
            )
            self.assert_("Sorry, we are unable to find any system with name" in response.data,
                         "There should be no system in the Neo4J database with the name: " + searchParam)
            # Search For System With System Name As Parameter - Valid System Name &
            searchParam = "system"
            response = client.post(
                "/social/systems",
                data=dict(txtSystemName=searchParam)
            )
            self.assert_(searchParam in response.data,
                         "There should be system in the Neo4J database with the name: " + searchParam)

    if __name__ == "__main__":
        unittest.main()
