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
    list1 = [
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


@app.route('/displaymap')
def display_map():
    json_obj = [{"title": "System1", "lat": 59.3, "lng": 18.1, "description": "Tilpia, Lettuce"},
                    {"title": "System2", "lat": 59.9, "lng": 10.8, "description": "Tilapia, Tomatoes"},
                    {"title": "System3", "lat": 55.7, "lng": 12.6, "description": "Salmon, Potatoes"}]
    return render_template("/dav/maps.html", **locals())

######################################################################
##  Social Components API
######################################################################


if __name__ == "__main__":
    app.run(debug=True)