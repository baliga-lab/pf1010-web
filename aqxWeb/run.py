import os
from mysql.connector.pooling import MySQLConnectionPool

from flask import Flask, render_template

from dav.analytics_views import dav
from dav.analytics_views import init_dav
from sc.models import init_sc_app
from sc.views import social

# UI imports
from flask_bootstrap import Bootstrap
import frontend as ui
from frontend import frontend

from nav import nav

os.environ['AQUAPONICS_SETTINGS'] = "system_db.cfg"
# To hold db connection pool
app = Flask(__name__)
# Secret key for the Session
app.secret_key = os.urandom(24)
app.register_blueprint(dav, url_prefix='/dav')
app.register_blueprint(social, url_prefix='/social')
app.register_blueprint(frontend, url_prefix='')
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


@app.route('/')
def index():
    return render_template('index.html')


######################################################################
# render error page
######################################################################
@app.errorhandler(500)
def page_not_found(e):
    return render_template('error.html'), 500


# Common init method for application
if __name__ == "__main__":
    # Initialize the aquaponics db connection
    app.debug = True
    app.config.from_envvar('AQUAPONICS_SETTINGS')
    create_conn(app)
    init_dav(pool)
    ui.init_app(pool)
    # Intialize the social component global app instance
    init_sc_app(app)
    # Initialise UI's nav routing
    nav.init_app(app)
    app.run(debug=True)
