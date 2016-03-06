import os
import json
import unittest
from flask import Flask
from aqxWeb.sc.models import init_sc_app
from aqxWeb.sc.views import social

app = Flask(__name__)
app.config.from_pyfile("../../../aqxWeb/sc/settings.cfg")
app.secret_key = os.urandom(24)
app.register_blueprint(social, url_prefix='/social')
init_sc_app(app)


class ScAPITest(unittest.TestCase):
    # Test Data For The Unit Test
    global sql_id
    global google_id
    global jsonObject
    sql_id = 40629
    google_id = "109635381067589243678"
    result = {
        "sql_id": sql_id,
        "google_id": google_id,
        "email": "bvenkatesh.tec@gmail.com",
        "givenName": "Venkatesh",
        "familyName": "Balasubramanian",
        "displayName": "Rahul Bala",
        "gender": "male",
        "dob": "03/19/1989",
        "user_type": "farmer",
        "status": 0
    }
    jsonObject = json.dumps({'user': result})

    # Ensure /aqxapi/put/user works as expected
    def test_create_user(self):
        with app.test_client() as client:
            response = client.post('/social/aqxapi/put/user', data=jsonObject, content_type='application/json')

    # Ensure /aqxapi/get/user/logged_in_user/ works as expected
    def test_get_logged_in_user(self):
        with app.test_client() as client:
            response = client.get('/social/aqxapi/get/user/logged_in_user/')
            # Negative Testing - Not Logged In User Trying To Get Their User Details
            result = json.loads(response.data)
            user = result.get('user')
            if user is not None:
                self.assert_('sql_id' not in user.keys(),
                             "Guest users should not be able to get their user JSON object")
            # Positive Testing - User Logged In And Trying To Get Their User Details
            with client.session_transaction() as session:
                session['uid'] = sql_id
            response = client.get('/social/aqxapi/get/user/logged_in_user/')
            result = json.loads(response.data)
            user = result.get('user')
            if user is not None:
                if user.get('sql_id') is not None:
                    self.assert_('google_id' in user.keys(), "user JSON object should contain google_id")
                    self.assert_('email' in user.keys(), "user JSON object should contain email")
                    self.assert_('givenName' in user.keys(), "user JSON object should contain givenName")
                    self.assert_('familyName' in user.keys(), "user JSON object should contain familyName")
                    self.assert_('displayName' in user.keys(), "user JSON object should contain displayName")
                    self.assert_('gender' in user.keys(), "user JSON object should contain gender")
                    self.assert_('dob' in user.keys(), "user JSON object should contain dob")
                    self.assert_('user_type' in user.keys(), "user JSON object should contain user_type")
                    self.assert_('status' in user.keys(), "user JSON object should contain status")

    # Ensure /aqxapi/get/user/by_google_id/<google_id> works as expected
    def test_get_user_by_google_id(self):
        with app.test_client() as client:
            response = client.get('/social/aqxapi/get/user/by_google_id/123epcbcd')
            # Negative Testing - Invalid google_id
            result = json.loads(response.data)
            user = result.get('user')
            if user is not None:
                self.assert_('sql_id' not in user.keys(),
                             "Invalid google id should return empty user json object")
            # Positive Testing - Valid google_id
            response = client.get('/social/aqxapi/get/user/by_google_id/' + google_id)
            result = json.loads(response.data)
            user = result.get('user')
            if user is not None:
                if user.get('sql_id') is not None:
                    self.assert_('google_id' in user.keys(), "user JSON object should contain google_id")
                    self.assert_('email' in user.keys(), "user JSON object should contain email")
                    self.assert_('givenName' in user.keys(), "user JSON object should contain givenName")
                    self.assert_('familyName' in user.keys(), "user JSON object should contain familyName")
                    self.assert_('displayName' in user.keys(), "user JSON object should contain displayName")
                    self.assert_('gender' in user.keys(), "user JSON object should contain gender")
                    self.assert_('dob' in user.keys(), "user JSON object should contain dob")
                    self.assert_('user_type' in user.keys(), "user JSON object should contain user_type")
                    self.assert_('status' in user.keys(), "user JSON object should contain status")

    # Ensure /aqxapi/get/user/by_google_id/<sql_id> works as expected
    def test_get_user_by_sql_id(self):
        with app.test_client() as client:
            response = client.get('/social/aqxapi/get/user/by_sql_id/123pxewbcd')
            # Negative Testing - Invalid sql_id
            result = json.loads(response.data)
            self.assert_('error' in result.keys(),
                         "Error JSON object should be returned indicating that the sql_id provided is not a valid format")
            # Positive Testing - Valid sql_id
            response = client.get('/social/aqxapi/get/user/by_sql_id/' + str(sql_id))
            result = json.loads(response.data)
            user = result.get('user')
            if user is not None:
                if user.get('sql_id') is not None:
                    self.assert_('google_id' in user.keys(), "user JSON object should contain google_id")
                    self.assert_('email' in user.keys(), "user JSON object should contain email")
                    self.assert_('givenName' in user.keys(), "user JSON object should contain givenName")
                    self.assert_('familyName' in user.keys(), "user JSON object should contain familyName")
                    self.assert_('displayName' in user.keys(), "user JSON object should contain displayName")
                    self.assert_('gender' in user.keys(), "user JSON object should contain gender")
                    self.assert_('dob' in user.keys(), "user JSON object should contain dob")
                    self.assert_('user_type' in user.keys(), "user JSON object should contain user_type")
                    self.assert_('status' in user.keys(), "user JSON object should contain status")


    # Ensure /aqxapi/delete/user/<sql_id> works as expected
    def test_delete_user(self):
        with app.test_client() as client:
            with client.session_transaction() as session:
                session['siteadmin'] = "true"
            response = client.delete('/social/aqxapi/delete/user/' + str(sql_id))

    if __name__ == "__main__":
        unittest.main()
