import unittest
from aqxWeb import run
from flask_nav import Nav
from aqxWeb import nav
from aqxWeb.sc import views,models
from mock import patch
import sys
import os
from flask import Flask


class FlaskTestCase(unittest.TestCase):

    def setUp(self):
        run.app.config['TESTING']= True
        run.app.config['DEBUG']= True
        #run.app.register_blueprint(views.social, url_prefix='/social')
        run.app.config['BOOTSTRAP_SERVE_LOCAL'] = True
        self.app = run.app.test_client()
        run.init_sc_app(run.app)


    @patch('flask.templating._render', return_value='View_pending_friend_request_works_fine')
    def test_view_pending_friend_request(self,mocked):
        with self.app as client :
            with client.session_transaction() as session:
                session['uid']=33
                print(session)
                print(run.app.config)
            res=client.get('/social/pendingRequest')
            print(client)

    @patch('flask.templating._render', return_value='Send_friend_request_works_fine')
    def test_send_friend_request(self,mocked):
        with self.app as client :
            with client.session_transaction() as session:
                session['uid']=33
                print(session)
                print(run.app.config)

            res=client.post('/social/send_friend_request/30')
            print(client)





if __name__ == '__main__':
    unittest.main()

