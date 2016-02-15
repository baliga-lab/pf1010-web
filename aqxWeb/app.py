#import sys
#sys.path.insert(0,'/dav/api')
#import app_dav

import json

from dav.dao.system import get_systems
from flask import Flask,jsonify,render_template
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
@app.route('/aqxapi/test/json')
def test():
    # This is a dummy list, 2 nested arrays containing some
    # params and values
    list = [
        {'param': 'foo', 'val': 2},
        {'param': 'bar', 'val': 10}
    ]
    # jsonify will do for us all the work, returning the
    # previous data structure in JSON
    return jsonify(results=list)


@app.route('/aqxapi/get/systems')
def get_all_systems():
   print get_systems();
   #return 'data printed';
   #return jsonify(systems=get_systems())
   systems=get_systems()

   system = systems[0]
   return system[0];

#   obj = {'systems' : get_systems()}
#  return json.dump(obj)

######################################################################
##  Social Components API
######################################################################


if __name__ == "__main__":
    app.run(debug=True)