import unittest
from aqxWeb import run
from flask_nav import Nav
from aqxWeb import nav
from aqxWeb.sc import views, models
from mock import patch
import sys
import os
from flask import Flask


class FlaskTestCase(unittest.TestCase):
    global sql_id
    sql_id = 29
    global google_id
    google_id = "108605381067579043278"
    global system_uid
    system_uid = "2e79ea8a411011e5aac7000c29b92d09"

    def setUp(self):
        run.app.config['TESTING'] = True
        run.app.config['DEBUG'] = True
        # run.app.register_blueprint(views.social, url_prefix='/social')
        run.app.config['BOOTSTRAP_SERVE_LOCAL'] = True
        self.app = run.app.test_client()
        run.init_sc_app(run.app)

    @patch('flask.templating._render', return_value='View_pending_friend_request_works_fine')
    def test_view_pending_friend_request(self, mocked):
        with self.app as client:
            with client.session_transaction() as session:
                session['uid'] = 33
            res = client.get('/social/pendingRequest')
            # print(res.data)

    @patch('flask.templating._render', return_value='Send_friend_request_works_fine')
    def test_send_friend_request(self, mocked):
        with self.app as client:
            with client.session_transaction() as session:
                session['uid'] = 33
            res = client.post('/social/send_friend_request/30')
            # print(res.data)

    @patch('flask.templating._render', return_value='Block a friend works fine')
    def test_block_friend(self, mocked):
        with self.app as client:
            with client.session_transaction() as session:
                session['uid'] = 33
            res = client.post('/social/block_friend/25')
            # print(res.data)

    @patch('flask.templating._render', return_value='UnBlock a friend works fine')
    def test_un_block_friend(self, mocked):
        with self.app as client:
            with client.session_transaction() as session:
                session['uid'] = 33
            res = client.post('/social/unblock_friend/25')
            # print(res.data)

    @patch('flask.templating._render', return_value='View my friends work fine')
    def test_un_block_friend(self, mocked):
        with self.app as client:
            with client.session_transaction() as session:
                session['uid'] = 33
            res = client.get('/social/friends')
            # print(res.data)

    @patch('flask.templating._render', return_value='Search for friends work fine')
    def test_search_friend(self, mocked):
        with self.app as client:
            with client.session_transaction() as session:
                session['uid'] = 33
            res = client.get('/social/searchFriends')
            # print(res.data)

    @patch('flask.templating._render', return_value='Get groups work fine')
    def test_get_groups(self, mocked):
        with self.app as client:
            with client.session_transaction() as session:
                session['uid'] = 33
            res = client.get('/social/groups')
            # print(res.data)

    @patch('flask.templating._render', return_value='Route To Search Systems Page Works As Expected')
    def test_search_systems_page_render(self, mocked):
        with self.app as client:
            with client.session_transaction() as session:
                session['uid'] = sql_id
            res = client.get('/social/systems/')
            print(res.data)
            self.assertTrue(mocked.called, "Route To Search Systems Page Failed: " + res.data)

    @patch('flask.templating._render', return_value='Search Systems Post Method Works As Expected')
    def test_search_systems(self, mocked):
        with self.app as client:
            with client.session_transaction() as session:
                session['uid'] = sql_id
            res = client.post('/social/systems/', data=dict(txtSystemName="isb"))
            print(res.data)
            self.assertTrue(mocked.called, "Search Systems Post Method Failed: " + res.data)

    @patch('flask.templating._render', return_value='Route To Manage Systems Page Works As Expected')
    def test_manage_systems_page_render(self, mocked):
        with self.app as client:
            with client.session_transaction() as session:
                session['uid'] = sql_id
            res = client.get('/social/manage/systems/' + system_uid)
            print(res.data)
            self.assertTrue(mocked.called, "Route To Manage Systems Page Failed: " + res.data)

    @patch('flask.templating._render', return_value='Approve/Reject Systems Participant Works As Expected')
    def test_manage_systems_approve_reject_participant(self, mocked):
        with self.app as client:
            with client.session_transaction() as session:
                session['uid'] = sql_id
            res = client.post('/social/systems/approve_reject_participant',
                              data=dict(system_uid=system_uid, google_id="234sdfdsf3w", submit="Approve"))
            self.assertFalse(mocked.called, "Approve Systems Participant Failed: " + res.data)
            res = client.post('/social/systems/approve_reject_participant',
                              data=dict(system_uid=system_uid, google_id="234sdfdsf3w", submit="Reject"))
            self.assertFalse(mocked.called, "Reject Systems Participant Failed: " + res.data)


if __name__ == '__main__':
    unittest.main()
