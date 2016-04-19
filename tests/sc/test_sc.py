import unittest
from aqxWeb import run
from mock import patch

class FlaskTestCase(unittest.TestCase):
    # Global Test Data For Unit Test Run
    global sql_id
    sql_id = 29
    global google_id
    google_id = "108605381067579043278"
    global system_uid
    system_uid = "2e79ea8a411011e5aac7000c29b92d09"
    global friend_request_sql_id
    friend_request_sql_id = 30
    global block_unblock_friend_sql_id
    block_unblock_friend_sql_id = 25
    global dummy_google_id
    dummy_google_id = "234sdfdsf3w"
    global search_system_name
    search_system_name = "isb"

    def setUp(self):
        run.app.config['TESTING'] = True
        run.app.config['DEBUG'] = True
        # run.app.register_blueprint(views.social, url_prefix='/social')
        run.app.config['BOOTSTRAP_SERVE_LOCAL'] = True
        self.app = run.app.test_client()
        run.init_sc_app(run.app)

    # Testing /friends route
    @patch('flask.templating._render', return_value='Route To Friends Page Works As Expected')
    def test_friends_page_loads(self, mocked):
        with self.app as client:
            with client.session_transaction() as session:
                session['uid'] = sql_id
        res = client.get('/social/friends')
        print(res.data)
        self.assertTrue(mocked.called, "Route To Friends Page Failed: " + res.data)

    @patch('flask.templating._render', return_value='View pending friend request works as expected')
    def test_view_pending_friend_request(self, mocked):
        with self.app as client:
            with client.session_transaction() as session:
                session['uid'] = sql_id
            res = client.get('/social/pendingRequest')
            print(res.data)
            self.assertTrue(mocked.called, "View_pending_friend_request failed: " + res.data)

    @patch('flask.templating._render', return_value='Send friend request works as expected')
    def test_send_friend_request(self, mocked):
        with self.app as client:
            with client.session_transaction() as session:
                session['uid'] = sql_id
            res = client.post('/social/send_friend_request/' + str(friend_request_sql_id))
            self.assertFalse(mocked.called, "Send_friend_request_works_fine failed: " + res.data)

    @patch('flask.templating._render', return_value='Block a friend works fine')
    def test_block_friend(self, mocked):
        with self.app as client:
            with client.session_transaction() as session:
                session['uid'] = sql_id
            res = client.post('/social/block_friend/' + str(block_unblock_friend_sql_id))
            self.assertFalse(mocked.called, "Block a friend failed: " + res.data)

    @patch('flask.templating._render', return_value='UnBlock a friend works as expected')
    def test_un_block_friend(self, mocked):
        with self.app as client:
            with client.session_transaction() as session:
                session['uid'] = sql_id
            res = client.post('/social/unblock_friend/' + str(block_unblock_friend_sql_id))
            print res.data
            self.assertFalse(mocked.called, "UnBlock a friend failed: " + res.data)

    @patch('flask.templating._render', return_value='Search Friends work as expected')
    def test_search_friend(self, mocked):
        with self.app as client:
            with client.session_transaction() as session:
                session['uid'] = sql_id
            res = client.get('/social/searchFriends')
            print(res.data)
            self.assertTrue(mocked.called, "Search Friends failed: " + res.data)

    @patch('flask.templating._render', return_value='Get Groups works as expected')
    def test_get_groups(self, mocked):
        with self.app as client:
            with client.session_transaction() as session:
                session['uid'] = sql_id
            res = client.get('/social/groups/')
            print(res.data)
            self.assertTrue(mocked.called, "Get Groups failed: " + res.data)

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
            res = client.post('/social/systems/', data=dict(txtSystemName=search_system_name))
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
                              data=dict(system_uid=system_uid, google_id=dummy_google_id, submit="Approve"))
            self.assertFalse(mocked.called, "Approve Systems Participant Failed: " + res.data)
            res = client.post('/social/systems/approve_reject_participant',
                              data=dict(system_uid=system_uid, google_id=dummy_google_id, submit="Reject"))
            self.assertFalse(mocked.called, "Reject Systems Participant Failed: " + res.data)


if __name__ == '__main__':
    unittest.main()
