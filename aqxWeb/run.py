from flask import Flask, render_template
from dav.views import dav
from sc.views import social

app = Flask(__name__)
app.register_blueprint(dav, url_prefix='/dav')
app.register_blueprint(social, url_prefix='/social')

@app.route('/')
def index():
    return render_template('aqxhomepage.html')

app.run(debug=True)

