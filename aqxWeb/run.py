from flask import Flask, render_template
from dav import views
from dav.views import dav


#from sc.views import social

app = Flask(__name__, static_folder=None)
app.register_blueprint(dav, url_prefix='/dav')
#app.register_blueprint(social, url_prefix='/social')

# @app.route('/')
# def index():
#     return render_template('aqxhomepage.html')

@app.route('/')
def root():
    return app.send_static_file('aqxhomepage.html')


views.init_app()
app.run(debug=True)

