from flask import Flask, render_template
from dav import analyticsViews
from dav.analyticsViews import dav
from sc.models import init_sc_app
from sc.views import social
import os

os.environ['AQUAPONICS_SETTINGS'] = "dav/system_db.cfg"

app = Flask(__name__)
# Secret key for the Session
app.secret_key = os.urandom(24)
app.register_blueprint(dav, url_prefix='/dav')
app.register_blueprint(social, url_prefix='/social')

# Social Component DB Configuration Settings
app.config.from_pyfile("sc/settings.cfg")

@app.route('/')
def index():
    return render_template('aqxhomepage.html')

# Common init method for application
if __name__ == "__main__":
    # Initialize the aquaponics db connection
    analyticsViews.init_app(app)
    # Intialize the social component global app instance
    init_sc_app(app)
    app.run(debug=True)
