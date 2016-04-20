import unittest
from aqxWeb import run
from mock import patch


class FlaskTestCase(unittest.TestCase):
    # Global Test Data For Unit Test Run
    global sql_id
    sql_id = 29
    global google_id
    google_id = "108605381067579043278"
    global group_uid
    group_uid = "106dfa22-f8df-4ef0-9302-d690ecc1c059"
    global group_name
    group_name = "Boston Social Team Group"
    global group_description
    group_description = "Social Team Private Group"
    global is_private_group
    is_private_group = "true"
    global system_uid
    system_uid = "2e79ea8a411011e5aac7000c29b92d09"
    global friend_request_sql_id
    friend_request_sql_id = 51
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
        run.init_dav_app(run.app)

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

    @patch('flask.templating._render', return_value='View Group Page Render Works As Expected')
    def test_view_group_page_render(self, mocked):
        with self.app as client:
            with client.session_transaction() as session:
                session['uid'] = sql_id
            res = client.get('/social/groups/' + group_uid)
            print(res.data)
            self.assertTrue(mocked.called, "View Group Page Render Failed: " + res.data)

    @patch('flask.templating._render', return_value='Route To Manage Group Page Works As Expected')
    def test_manage_group_page_render(self, mocked):
        with self.app as client:
            with client.session_transaction() as session:
                session['uid'] = sql_id
            res = client.get('/social/manage/groups/' + group_uid)
            print(res.data)
            self.assertTrue(mocked.called, "Route To Manage Group Page Failed: " + res.data)

    @patch('flask.templating._render', return_value='Update Group Information Works As Expected')
    def test_update_group_info(self, mocked):
        with self.app as client:
            with client.session_transaction() as session:
                session['uid'] = sql_id
            res = client.post('/manage/groups/update_group_info',
                              data=dict(group_uid=group_uid, name=group_name, description=group_description,
                                        is_private_group=is_private_group))
            self.assertFalse(mocked.called, "Update Group Information Failed: " + res.data)

    @patch('flask.templating._render', return_value='Approve/Reject Group Member Works As Expected')
    def test_group_approve_reject_member(self, mocked):
        with self.app as client:
            with client.session_transaction() as session:
                session['uid'] = sql_id
            res = client.post('/social/manage/groups/approve_reject_member',
                              data=dict(group_uid=group_uid, google_id=dummy_google_id, submit="Approve"))
            self.assertFalse(mocked.called, "Approve Group Member Failed: " + res.data)
            res = client.post('/social/manage/groups/approve_reject_member',
                              data=dict(group_uid=group_uid, google_id=dummy_google_id, submit="Reject"))
            self.assertFalse(mocked.called, "Reject Group Member Failed: " + res.data)

    @patch('flask.templating._render', return_value='Delete Admin Of A Group Works As Expected')
    def test_delete_group_admin(self, mocked):
        with self.app as client:
            with client.session_transaction() as session:
                session['uid'] = sql_id
            res = client.post('/social/manage/groups/delete_admin',
                              data=dict(group_uid=group_uid, google_id=dummy_google_id, submit="DeleteAdmin"))
            self.assertFalse(mocked.called, "Delete Admin Of A Group Failed: " + res.data)

    @patch('flask.templating._render',
           return_value='Delete Group Member & Make Group Member As Admin Works As Expected')
    def test_delete_group_member_or_make_admin(self, mocked):
        with self.app as client:
            with client.session_transaction() as session:
                session['uid'] = sql_id
            res = client.post('/social/manage/groups/delete_member_or_make_admin',
                              data=dict(group_uid=group_uid, google_id=dummy_google_id, submit="DeleteMember"))
            self.assertFalse(mocked.called, "Delete Group Member Failed: " + res.data)
            res = client.post('/social/manage/groups/delete_member_or_make_admin',
                              data=dict(group_uid=group_uid, google_id=dummy_google_id, submit="MakeAdmin"))
            self.assertFalse(mocked.called, "Make Group Member as Admin Failed: " + res.data)

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

    @patch('flask.templating._render', return_value='Route To System Page Works As Expected')
    def test_view_system_page_render(self, mocked):
        with self.app as client:
            with client.session_transaction() as session:
                session['uid'] = sql_id
            res = client.get('/social/systems/' + system_uid)
            print(res.data)
            self.assertTrue(mocked.called, "Route To System Page Failed: " + res.data)

    @patch('flask.templating._render', return_value='Route To Manage System Page Works As Expected')
    def test_manage_systems_page_render(self, mocked):
        with self.app as client:
            with client.session_transaction() as session:
                session['uid'] = sql_id
            res = client.get('/social/manage/systems/' + system_uid)
            print(res.data)
            self.assertTrue(mocked.called, "Route To Manage System Page Failed: " + res.data)

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

    @patch('flask.templating._render', return_value='Participate/Subscribe/Leave System Works As Expected')
    def test_participate_subscribe_leave_system(self, mocked):
        with self.app as client:
            with client.session_transaction() as session:
                session['uid'] = sql_id
            res = client.post('/social/systems/participate_subscribe_leave',
                              data=dict(system_uid=system_uid, google_id=dummy_google_id, submit="Subscribe"))
            self.assertFalse(mocked.called, "Subscribe For System Failed: " + res.data)
            res = client.post('/social/systems/participate_subscribe_leave',
                              data=dict(system_uid=system_uid, google_id=dummy_google_id, submit="Participate"))
            self.assertFalse(mocked.called, "Participate For System Failed: " + res.data)
            res = client.post('/social/systems/participate_subscribe_leave',
                              data=dict(system_uid=system_uid, google_id=dummy_google_id, submit="Leave"))
            self.assertFalse(mocked.called, "Leave System Failed: " + res.data)

    @patch('flask.templating._render', return_value='Delete or Make Admin / System Participant Works As Expected')
    def test_delete_system_participant_or_make_admin(self, mocked):
        with self.app as client:
            with client.session_transaction() as session:
                session['uid'] = sql_id
            res = client.post('/social/manage/systems/delete_system_participant_or_make_admin',
                              data=dict(system_uid=system_uid, google_id=dummy_google_id, submit="DeleteParticipant"))
            self.assertFalse(mocked.called, "Delete System Participant Failed: " + res.data)
            res = client.post('/social/manage/systems/delete_system_participant_or_make_admin',
                              data=dict(system_uid=system_uid, google_id=dummy_google_id, submit="MakeSubscriber"))
            self.assertFalse(mocked.called, "Make System Participant as Subscriber Failed: " + res.data)
            res = client.post('/social/manage/systems/delete_system_participant_or_make_admin',
                              data=dict(system_uid=system_uid, google_id=dummy_google_id, submit="MakeAdmin"))
            self.assertFalse(mocked.called, "Make System Participant as Admin Failed: " + res.data)

    @patch('flask.templating._render', return_value='Delete Admin Of A System Works As Expected')
    def test_delete_system_admin(self, mocked):
        with self.app as client:
            with client.session_transaction() as session:
                session['uid'] = sql_id
            res = client.post('/social/manage/systems/delete_admin',
                              data=dict(system_uid=system_uid, google_id=dummy_google_id, submit="DeleteAdmin"))
            self.assertFalse(mocked.called, "Delete Admin Of A System Failed: " + res.data)

    @patch('flask.templating._render', return_value='Delete or Make Admin / System Subscriber Works As Expected')
    def test_delete_system_subscriber_or_make_admin(self, mocked):
        with self.app as client:
            with client.session_transaction() as session:
                session['uid'] = sql_id
            res = client.post('/social/manage/systems/delete_system_subscriber_or_make_admin',
                              data=dict(system_uid=system_uid, google_id=dummy_google_id, submit="DeleteSubscriber"))
            self.assertFalse(mocked.called, "Delete System Subscriber Failed: " + res.data)
            res = client.post('/social/manage/systems/delete_system_subscriber_or_make_admin',
                              data=dict(system_uid=system_uid, google_id=dummy_google_id, submit="MakeParticipant"))
            self.assertFalse(mocked.called, "Make System Subscriber as Participant Failed: " + res.data)
            res = client.post('/social/manage/systems/delete_system_subscriber_or_make_admin',
                              data=dict(system_uid=system_uid, google_id=dummy_google_id, submit="MakeAdmin"))
            self.assertFalse(mocked.called, "Make System Subscriber as Admin Failed: " + res.data)


if __name__ == '__main__':
    unittest.main()
