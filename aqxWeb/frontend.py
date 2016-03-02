from flask import Blueprint, render_template, request

frontend = Blueprint('frontend', __name__, template_folder='templates',static_folder='static')


@frontend.route('/')
#######################################################################################
# function : index
# purpose : renders home page when user is not logged in
# parameters : None
# returns: index.html page
#######################################################################################
def index():
    user = request.cookies.get('user')
    return render_template('index.html')


@frontend.route('/newsfeed')
#######################################################################################
# function : newsfeed
# purpose : renders newsfeed (not yet integrating Soc components)
# parameters : None
# returns: newsfeed.html page currently -- soc components integration eventually
#######################################################################################
def newsfeed():
    return render_template('newsfeed.html')



@frontend.route('/about')
#######################################################################################
# function : about
# purpose : renders about page with same information from current aquaponics page
# parameters : None
# returns: about.html page
#######################################################################################
def about():
    return render_template('about.html')


@frontend.route('/systems')
#######################################################################################
# function : systems
# purpose : renders list of all systems belonging to user (not yet finished making)
# parameters : None
# returns: systems.html with same exact format as system.html
#######################################################################################
def systems():
    return render_template('systems.html')


@frontend.route('/system')
#######################################################################################
# function : system
# purpose : renders single system overview page (not yet integrating DAV components)
# parameters : None
# returns: system.html page currently -- DAV components integration eventually
#######################################################################################
def system():
    return render_template('system.html')


@frontend.route('/settings')
#######################################################################################
# function : settings
# purpose : renders settings page
# parameters : None
# returns: settings.html
#######################################################################################
def settings():
    return render_template('settings.html')


@frontend.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        if valid_login(request.form['username'],
                       request.form['password']):
            return log_the_user_in(request.form['username'])
        else:
            error = 'Invalid username/password'
    # executed when request method is GET or when credentials are invalid
    return render_template('login.html', error=error)


@frontend.route('/coming')
#######################################################################################
# function : coming soon
# purpose : placeholder for pages not yet designed -- will remove later
# parameters : None
# returns: coming.html
#######################################################################################
def coming():
    return render_template('coming.html')