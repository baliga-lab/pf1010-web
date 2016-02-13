import MySQLdb
from flask import Flask

app = Flask(__name__)
#app.config.from_envvar('AQUAPONICS_SETTINGS')

app.config['HOST'] = 'localhost'
app.config['USER'] = 'aquaponics'
app.config['PASS'] = 'aquaponics'
app.config['DB']   = 'aquaponics'


def dbconn():
    #return MySQLdb.connect(host=app.config['HOST'], user=app.config['USER'],
    #                       passwd=app.config['PASS'], db=app.config['DB'])
    return MySQLdb.connect(host='localhost', user='root',
                           passwd='horses', db='aquaponics')


def get_systems():
    conn = dbconn();
    cursor = conn.cursor();
    query = ("select s.system_uid,u.id as user_id,u.default_site_location_lat,u.default_site_location_lng "
             "from systems s "
             "join users u on s.user_id = u.id")

    try:
       cursor.execute(query)
       rows = cursor.fetchall()

    finally:
        cursor.close()
        conn.close()

    return rows

# locations = [
#     {
#         'system_uid': '316f3f2e3fe411e597b1000c29b92d09'',
#         'name': 'My first system',
#         'default_site_location_lat': 47.6225770000
#         'default_site_location_lng': -122.3374360000
#     },
#     {
#         'id': 2,
#         'title': u'Learn Python',
#         'description': u'Need to find a good Python tutorial on the web',
#         'done': False
#     }
# ]