import os

from flask import Flask, render_template

from dav import analyticsViews
from dav.analyticsViews import dav
from sc.models import init_sc_app
from sc.views import social

# UI imports
from flask_bootstrap import Bootstrap
import frontend as x
from frontend import frontend

from nav import nav

os.environ['AQUAPONICS_SETTINGS'] = "dav/system_db.cfg"

app = Flask(__name__)
# Secret key for the Session
app.secret_key = os.urandom(24)
app.register_blueprint(dav, url_prefix='/dav')
app.register_blueprint(social, url_prefix='/social')
app.register_blueprint(frontend, url_prefix='')

# Social Component DB Configuration Settings
app.config.from_pyfile("sc/settings.cfg")
app.config['BOOTSTRAP_SERVE_LOCAL'] = True
Bootstrap(app)


@app.route('/')
def index():
    return render_template('index.html')

# Common init method for application
if __name__ == "__main__":
    # Initialize the aquaponics db connection
    analyticsViews.init_app(app)
    x.init_app(app)
    # Intialize the social component global app instance
    init_sc_app(app)
    # Initialise UI's nav routing
    nav.init_app(app)
    app.run(debug=True)
