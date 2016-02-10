from dav.app.system import get_all_systems
from flask import Flask, render_template
app = Flask(__name__)

######################################################################
##  UI API
######################################################################

@app.route('/')
@app.route('/index')
def index():
    user = {'nickname': 'Alice'}  # fake user
    return render_template("index.html",
                           title='Home',
                           user=user)

######################################################################
##  Data Analytics and Viz. API
######################################################################



@app.route('/aqxapi/get/systems')
def get_systems():
    return get_all_systems()

######################################################################
##  Social Components API
######################################################################


if __name__ == "__main__":
    app.run(debug=True)