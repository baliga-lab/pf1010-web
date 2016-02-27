from flask import Flask, render_template
from dav import analyticsViews
from dav.analyticsViews import dav
import os
#from sc.views import social
os.environ['AQUAPONICS_SETTINGS'] = "dav/system_db.cfg"

app = Flask(__name__)
app.register_blueprint(dav, url_prefix='/dav')
#app.register_blueprint(social, url_prefix='/social')

# Initialize the aquaponics db connection


@app.route('/')
def index():
    return render_template('aqxhomepage.html')

# Common init method for application
if __name__ == "__main__":
    analyticsViews.init_app(app)
    app.run(debug=True)
