import os
from mysql.connector.pooling import MySQLConnectionPool
from flask import url_for
from flask import Flask, render_template,redirect
from flask import session
from flask_oauth import OAuth

# UI imports
from flask_bootstrap import Bootstrap
from frontend import frontend as ui
from servicesV2 import init_app as init_ui_app2
from nav import nav
import views

# DAV imports
from dav.analytics_views import dav
from dav.analytics_views import init_dav as init_dav_app

# Social imports
from sc.models import init_sc_app
from sc.views import social

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

#OAuth Configuration Settings
app.config.from_pyfile("OAuth_Settings.cfg")

Bootstrap(app)

@app.route('/')
def index():
    return render_template('index.html')


######################################################################
# render error page
######################################################################
@app.errorhandler(500)
def page_not_found(e):
    return render_template('error.html'), 500


oauth = OAuth()


google = oauth.remote_app('google',
                          base_url='https://www.google.com/accounts/',
                          authorize_url='https://accounts.google.com/o/oauth2/auth',
                          request_token_url=None,
                          request_token_params={
                              'scope': 'https://www.googleapis.com/auth/userinfo.email https://www.googleapis.com/auth/plus.login',
                              'response_type': 'code'},
                          access_token_url='https://accounts.google.com/o/oauth2/token',
                          access_token_method='POST',
                          access_token_params={'grant_type': 'authorization_code'},
                          consumer_key=app.config['CONSUMER_KEY'],
                          consumer_secret=app.config['CONSUMER_SECRET'])

@app.route('/getToken')
def getToken():
    callback = url_for('authorized', _external=True)
    return google.authorize(callback=callback)


@app.route('/oauth2callback')
@google.authorized_handler
def authorized(resp):
    access_token = resp['access_token']
    # print(access_token)
    session['access_token'] = access_token, ''
    session['token'] = access_token
    return redirect(url_for('Home'))


@app.route('/dav/social/Home')
@app.route('/social/Home')
@app.route('/Home')
#######################################################################################
# function : home
# purpose : renders userData.html
# parameters : None
# returns: userData.html page
#######################################################################################
def Home():
    access_token = session.get('access_token')
    if access_token is None:
        return redirect(url_for('getToken'))

    access_token = access_token[0]
    from urllib2 import Request, urlopen, URLError

    headers = {'Authorization': 'OAuth ' + access_token}
    req = Request('https://www.googleapis.com/oauth2/v1/userinfo',
                  None, headers)
    try:
        res = urlopen(req)
    except URLError, e:
        if e.code == 401:
            # Unauthorized - bad token
            session.pop('access_token', None)
            return redirect(url_for('getToken'))
    return redirect(url_for('social.signin'))


# Common init method for application
if __name__ == "__main__":
    app.debug = True
    app.config.from_envvar('AQUAPONICS_SETTINGS')
    init_ui_app2(app)
    init_dav_app(app)
    init_sc_app(app)
    nav.init_app(app)
    app.run(debug=True)