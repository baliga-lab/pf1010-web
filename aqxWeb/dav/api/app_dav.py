from flask import Flask,jsonify
import json
from system import get_systems
app = Flask(__name__)


@app.route('/')
def index():
    return 'Hello AQX !'

@app.route('/test')
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


@app.route(''/aqxapi/get/systems)
def get_all_systems():
   print get_systems();
   #return 'data printed';
   #return jsonify(systems=get_systems())
   systems=get_systems()

   system = systems[0]
   return system[0];

#   obj = {'systems' : get_systems()}
#  return json.dump(obj)




if __name__ == "__main__":
    app.run(debug=True)