import os
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

    def test_get_logged_in_user(self):
        with app.test_client() as client:
            response = client.get('/social/aqxapi/get/user/logged_in_user/')
            print response.data
            # Page Load Negative Testing
            self.assert_("Gender" not in response.data, "Guest user will not be able to access the search systems page")
            with client.session_transaction() as session:
                session['uid'] = 29
            response = client.get('/social/aqxapi/get/user/logged_in_user/')
            print response.data

    if __name__ == "__main__":
        unittest.main()
