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


class ScSystemDAOTest(unittest.TestCase):


    if __name__ == "__main__":
        unittest.main()
