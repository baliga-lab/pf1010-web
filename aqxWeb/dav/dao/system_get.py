import MySQLdb
from flask import Flask

app = Flask(__name__)

app.config['HOST'] = 'localhost'
app.config['USER'] = 'aquaponics'
app.config['PASS'] = 'aquaponics'
app.config['DB']   = 'aquaponics'


def dbconn():
    return MySQLdb.connect(host=app.config['HOST'], user=app.config['USER'],
                           passwd=app.config['PASS'], db=app.config['DB'])


def get_systems():
    conn = dbconn();
    cursor = conn.cursor();
    query = ("select system_uid, user_id, location_lat ,location_lng "
             "from systems")

    try:
       cursor.execute(query)
       rows = cursor.fetchall()

    finally:
        cursor.close()
        conn.close()

    return rows