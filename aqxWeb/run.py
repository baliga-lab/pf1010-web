from flask import Flask, render_template
from flask_bootstrap import Bootstrap
from mysql.connector.pooling import MySQLConnectionPool

# UI imports
from frontend import frontend as ui
from services import init_app as init_ui_app
from servicesV2 import init_app as init_ui_app2
from nav import nav
import views

# DAV imports
from dav.analytics_views import dav
from dav.analytics_views import init_dav as init_dav_app

# Social imports
from sc.views import social
from sc.models import init_sc_app

import os


os.environ['AQUAPONICS_SETTINGS'] = "system_db.cfg"
# To hold db connection pool
app = Flask(__name__)
# Secret key for the Session
app.secret_key = os.urandom(24)
app.register_blueprint(dav, url_prefix='/dav')
app.register_blueprint(social, url_prefix='/social')
app.register_blueprint(ui, url_prefix='')
pool = None
# Social Component DB Configuration Settings
app.config.from_pyfile("sc/settings.cfg")
app.config['BOOTSTRAP_SERVE_LOCAL'] = True
Bootstrap(app)


######################################################################
# method to create connection pool to mySQL DB when application starts
######################################################################
def create_conn(app):
    global pool
    print("PID %d: initializing pool..." % os.getpid())
    dbconfig = {
        "host": app.config['HOST'],
        "user": app.config['USER'],
        "passwd": app.config['PASS'],
        "db": app.config['DB']
    }
    pool = MySQLConnectionPool(pool_name="mypool", pool_size=app.config['POOLSIZE'], **dbconfig)


######################################################################
# render error page
######################################################################
@app.errorhandler(500)
def page_not_found(e):
    return render_template('error.html'), 500


# Common init method for application
if __name__ == "__main__":
    app.debug = True
    app.config.from_envvar('AQUAPONICS_SETTINGS')
    create_conn(app)
    init_ui_app(pool) # includes api v1
    init_ui_app2(pool) # includes api v2
    init_dav_app(pool)
    init_sc_app(app)
    nav.init_app(app)
    app.run(debug=True)
