import os
import logging

from flask import url_for
from flask import Flask, render_template, redirect
from flask import session
from flask_oauth import OAuth

from flask_bootstrap import Bootstrap
from frontend import frontend as ui
from nav import nav
import views

from analytics.views import dav
from social.views import social

app = Flask(__name__)

app.config.from_envvar('AQUAPONICS_SETTINGS')

nav.init_app(app)

app.register_blueprint(dav, url_prefix='/dav')
app.register_blueprint(social, url_prefix='/social')
app.register_blueprint(ui, url_prefix='')
pool = None


Bootstrap(app)

@app.route('/')
def index():
    return render_template('index.html')


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

@app.route('/get-token')
def get_token():
    callback = url_for('authorized', _external=True)
    return google.authorize(callback=callback)


@app.route('/oauth2callback')
@google.authorized_handler
def authorized(resp):
    access_token = resp['access_token']
    session['access_token'] = access_token, ''
    session['token'] = access_token
    return redirect(url_for('home'))


@app.route('/dav/social/Home')
@app.route('/social/Home')
@app.route('/Home')
def home():
    access_token = session.get('access_token')
    if access_token is None:
        return redirect(url_for('get_token'))

    access_token = access_token[0]
    from urllib2 import Request, urlopen, URLError

    headers = {'Authorization': 'OAuth ' + access_token}
    req = Request('https://www.googleapis.com/oauth2/v1/userinfo',
                  None, headers)
    try:
        res = urlopen(req)
    except URLError as e:
        if e.code == 401:
            # Unauthorized - bad token
            session.pop('access_token', None)
            return redirect(url_for('get_token'))
    return redirect(url_for('social.signin'))


if __name__ == "__main__":
    handler = logging.StreamHandler()
    handler.setLevel(logging.INFO)

    app.debug = True
    app.logger.addHandler(handler)
    app.run(host='0.0.0.0')
