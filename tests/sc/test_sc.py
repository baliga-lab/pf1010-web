import unittest

from aqxWeb import run
from mock import patch
from py2neo import Node
from aqxWeb.sc import models
from aqxWeb.sc.models import System
from aqxWeb.sc.models import Group
from aqxWeb.sc.models import User



class FlaskTestCase(unittest.TestCase):
    def setUp(self):
        run.app.config['TESTING'] = True
        run.app.config['DEBUG'] = True
        run.app.config['BOOTSTRAP_SERVE_LOCAL'] = True
        self.app = run.app.test_client()
        run.init_sc_app(run.app)
        run.init_dav_app(run.app)

        # Do not change the test_user as it's the primary user to set session. If your test require
        # additional user, create separate node. Scroll down for more examples on System & Groups
        # --------------------------------------------------------------------------------------
        global sql_id
        sql_id = 19136
        global google_id
        google_id = "708635381087572041278"
        global test_user
        test_user = Node("User",
                         sql_id=sql_id, google_id=google_id, givenName="ISBTestUser", familyName="ISBTestUser",
                         displayName="ISBTestUser",
                         email="ISBTestUser@gmail.com", gender="male", dob="1989-03-19",
                         image_url="https://www.gstatic.com/webp/gallery3/1.png",
                         user_type="subscriber", organization="Northeastern University", creation_time=1461345863010,
                         modified_time=1461345863010, status=0)
        # --------------------------------------------------------------------------------------
        # Dummy User For System Participant/Subscriber
        # --------------------------------------------------------------------------------------
        global sql_id_user_system
        sql_id_user_system = 34729
        global google_id_user_system
        google_id_user_system = "208305386027599043578"
        global test_user_system
        test_user_system = Node("User",
                                sql_id=sql_id_user_system, google_id=google_id_user_system,
                                givenName="Test User For System",
                                familyName="Test User For System",
                                displayName="Test User For System",
                                email="ISBTestUser@gmail.com", gender="male", dob="1989-03-19",
                                image_url="https://www.gstatic.com/webp/gallery3/1.png",
                                user_type="subscriber", organization="Northeastern University",
                                creation_time=1461345863010,
                                modified_time=1461345863010, status=0)
        # --------------------------------------------------------------------------------------

     # --------------------------------------------------------------------------------------
        # Dummy User For Friends Testing
        # --------------------------------------------------------------------------------------
        global sql_id_user_friend
        sql_id_user_friend = 77729
        global google_id_user_friend
        google_id_user_friend = "208305386777777043578"
        global test_user_friend
        test_user_friend = Node("User",
                                sql_id=sql_id_user_friend, google_id=google_id_user_friend,
                                givenName="Test User For Friend",
                                familyName="Test User For Friend",
                                displayName="Test User For Friend",
                                email="ISBTestUserFriends@gmail.com", gender="female", dob="1980-07-20",
                                image_url="http://blog.boostability.com/wp-content/uploads/2014/09/Panda-Update.jpg",
                                user_type="subscriber", organization="Northeastern University",
                                creation_time=1461345863020,
                                modified_time=1461345863020, status=0)
        # --------------------------------------------------------------------------------------


        # Dummy System Node
        # --------------------------------------------------------------------------------------
        global system_id
        system_id = 4898231
        global system_uid
        system_uid = "4e79pa8a410011e5yac7000c29g93d09"
        global system_name
        system_name = "Unit Test Social System"
        global test_system_node
        test_system_node = Node("System", system_id=system_id, system_uid=system_uid, name=system_name,
                                description="Unit Test Social System Description", location_lat=42.338660,
                                location_lng=-71.092186, status=0, creation_time=1461345863010,
                                modified_time=1461345863010)
        # --------------------------------------------------------------------------------------


        # Dummy Group Information
        # --------------------------------------------------------------------------------------
        global group_uid
        group_uid = "853tfa22-f9de-4lf0-9302-z690ecp1c059"
        global group_name
        group_name = "Unit Test Social Team Group"
        global group_description
        group_description = "Unit Test Social Team Group Description"
        global is_private_group
        is_private_group = "true"
        global test_group_node
        test_group_node = Node("Group", group_uid=group_uid, group_name=group_name,
                               group_description=group_description, is_private_group=is_private_group,
                               status=0, creation_time=1461345863010,
                               modified_time=1461345863010)
        # --------------------------------------------------------------------------------------

        # Dummy User For Group Member/Pending_Member
        # --------------------------------------------------------------------------------------
        global sql_id_user_group
        sql_id_user_group = 58301
        global google_id_user_group
        google_id_user_group = "427395386123596043278"
        global test_user_group
        test_user_group = Node("User",
                               sql_id=sql_id_user_group, google_id=google_id_user_group,
                               givenName="Test User For Group",
                               familyName="Test User For Group",
                               displayName="Test User For Group",
                               email="ISBTestUser@gmail.com", gender="male", dob="1989-03-19",
                               image_url="https://www.gstatic.com/webp/gallery3/1.png",
                               user_type="subscriber", organization="Northeastern University",
                               creation_time=1461345863010,
                               modified_time=1461345863010, status=0)
        # --------------------------------------------------------------------------------------

        global graph
        graph = models.get_graph_connection_uri()

    # --------------------------------------------------------------------------------------
    # Friends Page Tests
    # --------------------------------------------------------------------------------------

    # Testing /friends route
    @patch('flask.templating._render', return_value='Route To Friends Page Works As Expected')
    def test_friends_page_loads(self, mocked):
        self.helper_create_user_node(test_user)
        with self.app as client:
            with client.session_transaction() as session:
                session['uid'] = test_user['sql_id']
        res = client.get('/social/friends')
        print(res.data)
        self.assertTrue(mocked.called, "Route To Friends Page Passed: " + res.data)
        self.helper_delete_user_node(test_user)

    @patch('flask.templating._render', return_value='View Pending Friends Request works as expected')
    def test_pending_friends(self, mocked):
        self.helper_create_user_node(test_user)
        with self.app as client:
            with client.session_transaction() as session:
                session['uid'] = test_user['sql_id']
        res = client.get('/social/pendingRequest')
        print(res.data)
        self.assertTrue(mocked.called, "View Pending Friends Request works as expected" + res.data)
        self.helper_delete_user_node(test_user)


    '''
    @patch('flask.templating._render', return_value='View pending friend request works as expected')
    def test_view_pending_friend_request(self, mocked):
        graph.create(test_user)
        with self.app as client:
            with client.session_transaction() as session:
                session['uid'] = test_user['sql_id']
            res = client.get('/social/pendingRequest')
            print(res.data)
            self.assertTrue(mocked.called, "View_pending_friend_request Passed: " + res.data)
        self.helper_delete_user_node(test_user)
        '''

    @patch('flask.templating._render', return_value='Recommended friend test works as expected')
    def test_reco_friend_request(self, mocked):
        self.helper_create_user_node(test_user)
        with self.app as client:
            with client.session_transaction() as session:
                session['uid'] = test_user['sql_id']
            res = client.get('/social/recofriends')
            print(res.data)
            self.assertTrue(mocked.called, "test_reco_friend_request Passed: " + res.data)
        self.helper_delete_user_node(test_user)

    '''

    # Create Separate nodes for testing send friend request something as follows:
    # self.helper_create_user_node(test_user)
    # self.helper_create_user_node(test_friend_request_user)
    # self.helper_delete_user_node(test_user)
    # self.helper_delete_user_node(test_friend_request_user)
    @patch('flask.templating._render', return_value='Send friend request works as expected')
    def test_send_friend_request(self, mocked):
        self.helper_create_user_node(test_user)
        with self.app as client:
            with client.session_transaction() as session:
                session['uid'] = test_user['sql_id']
            res = client.post('/social/send_friend_request/' + str(friend_request_sql_id))
            self.assertFalse(mocked.called, "Send_friend_request_works_fine passed: " + res.data)
        self.helper_delete_user_node(test_user)

    @patch('flask.templating._render', return_value='Block a friend works fine')
    def test_block_friend(self, mocked):
        self.helper_create_user_node(test_user)
        with self.app as client:
            with client.session_transaction() as session:
                session['uid'] = test_user['sql_id']
            res = client.post('/social/block_friend/' + str(block_unblock_friend_sql_id))
            self.assertFalse(mocked.called, "Block a friend failed: " + res.data)
        self.helper_delete_user_node(test_user)


    @patch('flask.templating._render', return_value='UnBlock a friend works as expected')
    def test_un_block_friend(self, mocked):
        self.helper_create_user_node(test_user)
        with self.app as client:
            with client.session_transaction() as session:
                session['uid'] = test_user['sql_id']
            res = client.post('/social/unblock_friend/' + str(block_unblock_friend_sql_id))
            self.assertFalse(mocked.called, "UnBlock a friend failed: " + res.data)
        self.helper_delete_user_node(test_user)
        '''

    @patch('flask.templating._render', return_value='Search Friends work as expected')
    def test_search_friend(self, mocked):
        self.helper_create_user_node(test_user)
        with self.app as client:
            with client.session_transaction() as session:
                session['uid'] = test_user['sql_id']
            res = client.get('/social/searchFriends')
            print(res.data)
            self.assertTrue(mocked.called, "Search Friends failed: " + res.data)
        self.helper_delete_user_node(test_user)

    @patch('flask.templating._render', return_value='Block Friend Works')
    def test_block_friend(self, mocked):
        self.helper_create_user_node(test_user)
        self.helper_create_user_node(test_user_friend)
        self.helper_make_friend(test_user_friend['sql_id'])
        with self.app as client:
            with client.session_transaction() as session:
                session['uid'] = test_user['sql_id']
            res = client.post('/social/block_friend/'+ str(test_user_friend['sql_id']))
            print(res.data)
            self.assertFalse(mocked.called, "Block Friends passed: " + res.data)
        self.helper_delete_friend(test_user_friend['sql_id'])
        self.helper_delete_user_node(test_user_friend)
        self.helper_delete_user_node(test_user)

    @patch('flask.templating._render', return_value='UnBlock Friend Works')
    def test_unblock_friend(self, mocked):
        self.helper_create_user_node(test_user)
        self.helper_create_user_node(test_user_friend)
        self.helper_make_friend(test_user_friend['sql_id'])
        with self.app as client:
            with client.session_transaction() as session:
                session['uid'] = test_user['sql_id']
            res = client.post('/social/block_friend/'+ str(test_user_friend['sql_id']))
            res2 = client.post('/social/unblock_friend/'+ str(test_user_friend['sql_id']))
            print(res.data)
            print(res2.data)
            self.assertFalse(mocked.called, "Block Friends passed: " + res.data)
        self.helper_delete_friend(test_user_friend['sql_id'])
        self.helper_delete_user_node(test_user_friend)
        self.helper_delete_user_node(test_user)



    # --------------------------------------------------------------------------------------
    # Groups Page Tests
    # --------------------------------------------------------------------------------------

    @patch('flask.templating._render', return_value='Get Groups works as expected')
    def test_get_groups(self, mocked):
        self.helper_create_user_node(test_user)
        with self.app as client:
            with client.session_transaction() as session:
                session['uid'] = test_user['sql_id']
            res = client.get('/social/groups/')
            print(res.data)
            self.assertTrue(mocked.called, "Get Groups failed: " + res.data)
        self.helper_delete_user_node(test_user)

    @patch('flask.templating._render', return_value='View Group Page Render Works As Expected')
    def test_view_group_page_render(self, mocked):
        self.helper_create_user_node(test_user)
        self.helper_create_group_node(test_group_node)
        with self.app as client:
            with client.session_transaction() as session:
                session['uid'] = test_user['sql_id']
            res = client.get('/social/groups/' + str(test_group_node['group_uid']))
            print(res.data)
            self.assertTrue(mocked.called, "View Group Page Render Failed: " + res.data)
        self.helper_delete_group_node(test_group_node)
        self.helper_delete_user_node(test_user)

    @patch('flask.templating._render', return_value='Route To Manage Group Page Works As Expected')
    def test_manage_group_page_render(self, mocked):
        self.helper_create_user_node(test_user)
        self.helper_create_group_node(test_group_node)
        self.helper_make_admin_for_group(test_user['google_id'], test_group_node['group_uid'])
        with self.app as client:
            with client.session_transaction() as session:
                session['uid'] = test_user['sql_id']
            res = client.get('/social/manage/groups/' + str(test_group_node['group_uid']))
            print(res.data)
            self.assertTrue(mocked.called, "Route To Manage Group Page Failed: " + res.data)
        self.helper_leave_group(test_user['google_id'], test_group_node['group_uid'])
        self.helper_delete_group_node(test_group_node)
        self.helper_delete_user_node(test_user)

    @patch('flask.templating._render', return_value='Update Group Information Works As Expected')
    def test_update_group_info(self, mocked):
        self.helper_create_user_node(test_user)
        self.helper_create_group_node(test_group_node)
        self.helper_make_admin_for_group(test_user['google_id'], test_group_node['group_uid'])
        with self.app as client:
            with client.session_transaction() as session:
                session['uid'] = test_user['sql_id']
            updated_group_name = str(test_group_node['name']) + " Updated"
            updated_group_description = str(test_group_node['description']) + " Updated"
            res = client.post('/social/manage/groups/update_group_info',
                              data=dict(group_uid=test_group_node['group_uid'],
                                        name=updated_group_name,
                                        description=updated_group_description,
                                        is_private_group=test_group_node['is_private_group']))
            self.assertFalse(mocked.called, "Update Group Information Failed: " + res.data)
        self.helper_leave_group(test_user['google_id'], test_group_node['group_uid'])
        self.helper_delete_group_node(test_group_node)
        self.helper_delete_user_node(test_user)

    @patch('flask.templating._render', return_value='Approve/Reject Group Member Works As Expected')
    def test_group_approve_reject_member(self, mocked):
        self.helper_create_user_node(test_user)
        self.helper_create_user_node(test_user_group)
        self.helper_create_group_node(test_group_node)
        self.helper_make_admin_for_group(test_user['google_id'], test_group_node['group_uid'])
        self.helper_make_pending_member_to_group(test_user_group['google_id'], test_group_node['group_uid'])
        with self.app as client:
            with client.session_transaction() as session:
                session['uid'] = test_user['sql_id']
            res = client.post('/social/manage/groups/approve_reject_member',
                              data=dict(group_uid=test_group_node['group_uid'],
                                        google_id=test_user_group['google_id'], submit="Approve"))
            self.assertFalse(mocked.called, "Approve Group Member Failed: " + res.data)

            self.helper_leave_group(test_user_group['google_id'], test_group_node['group_uid'])
            self.helper_make_pending_member_to_group(test_user_group['google_id'], test_group_node['group_uid'])
            res = client.post('/social/manage/groups/approve_reject_member',
                              data=dict(group_uid=test_group_node['group_uid'],
                                        google_id=test_user_group['google_id'], submit="Reject"))
            self.assertFalse(mocked.called, "Reject Group Member Failed: " + res.data)

        self.helper_leave_group(test_user['google_id'], test_group_node['group_uid'])
        self.helper_delete_group_node(test_group_node)
        self.helper_delete_user_node(test_user_group)
        self.helper_delete_user_node(test_user)

    @patch('flask.templating._render', return_value='Delete Admin Of A Group Works As Expected')
    def test_delete_group_admin(self, mocked):
        self.helper_create_user_node(test_user)
        self.helper_create_user_node(test_user_group)
        self.helper_create_group_node(test_group_node)
        self.helper_make_admin_for_group(test_user['google_id'], test_group_node['group_uid'])
        self.helper_make_admin_for_group(test_user_group['google_id'], test_group_node['group_uid'])
        with self.app as client:
            with client.session_transaction() as session:
                session['uid'] = test_user['sql_id']
            res = client.post('/social/manage/groups/delete_admin',
                              data=dict(group_uid=test_group_node['group_uid'],
                                        google_id=test_user_group['google_id'], submit="DeleteAdmin"))
            self.assertFalse(mocked.called, "Delete Admin Of A Group Failed: " + res.data)
        self.helper_leave_group(test_user['google_id'], test_group_node['group_uid'])
        self.helper_delete_group_node(test_group_node)
        self.helper_delete_user_node(test_user_group)
        self.helper_delete_user_node(test_user)

    @patch('flask.templating._render',
           return_value='Delete Group Member & Make Group Member As Admin Works As Expected')
    def test_delete_group_member_or_make_admin(self, mocked):
        self.helper_create_user_node(test_user)
        self.helper_create_user_node(test_user_group)
        self.helper_create_group_node(test_group_node)
        self.helper_make_admin_for_group(test_user['google_id'], test_group_node['group_uid'])
        self.helper_make_member_to_group(test_user_group['google_id'], test_group_node['group_uid'])
        with self.app as client:
            with client.session_transaction() as session:
                session['uid'] = test_user['sql_id']
            res = client.post('/social/manage/groups/delete_member_or_make_admin',
                              data=dict(group_uid=test_group_node['group_uid'],
                                        google_id=test_user_group['google_id'], submit="DeleteMember"))
            self.assertFalse(mocked.called, "Delete Group Member Failed: " + res.data)

            self.helper_make_member_to_group(test_user_group['google_id'], test_group_node['group_uid'])
            res = client.post('/social/manage/groups/delete_member_or_make_admin',
                              data=dict(group_uid=test_group_node['group_uid'],
                                        google_id=test_user_group['google_id'], submit="MakeAdmin"))
            self.assertFalse(mocked.called, "Make Group Member as Admin Failed: " + res.data)

        self.helper_leave_group(test_user_group['google_id'], test_group_node['group_uid'])
        self.helper_leave_group(test_user['google_id'], test_group_node['group_uid'])
        self.helper_delete_group_node(test_group_node)
        self.helper_delete_user_node(test_user_group)
        self.helper_delete_user_node(test_user)

    # --------------------------------------------------------------------------------------
    # System Page Tests
    # --------------------------------------------------------------------------------------

    @patch('flask.templating._render', return_value='Route To Search Systems Page Works As Expected')
    def test_search_systems_page_render(self, mocked):
        self.helper_create_user_node(test_user)
        with self.app as client:
            with client.session_transaction() as session:
                session['uid'] = test_user['sql_id']
            res = client.get('/social/systems/')
            print(res.data)
            self.assertTrue(mocked.called, "Route To Search Systems Page Failed: " + res.data)
        self.helper_delete_user_node(test_user)

    @patch('flask.templating._render', return_value='Search Systems Post Method Works As Expected')
    def test_search_systems(self, mocked):
        self.helper_create_user_node(test_user)
        self.helper_create_system_node(test_system_node)
        with self.app as client:
            with client.session_transaction() as session:
                session['uid'] = test_user['sql_id']
            res = client.post('/social/systems/', data=dict(txtSystemName=system_name))
            print(res.data)
            self.assertTrue(mocked.called, "Search Systems Post Method Failed: " + res.data)
        self.helper_delete_system_node(test_system_node)
        self.helper_delete_user_node(test_user)

    @patch('flask.templating._render', return_value='Route To System Page Works As Expected')
    def test_view_system_page_render(self, mocked):
        self.helper_create_user_node(test_user)
        self.helper_create_system_node(test_system_node)
        with self.app as client:
            with client.session_transaction() as session:
                session['uid'] = test_user['sql_id']
            res = client.get('/social/systems/' + str(system_uid))
            print(res.data)
            self.assertTrue(mocked.called, "Route To System Page Failed: " + res.data)
        self.helper_delete_system_node(test_system_node)
        self.helper_delete_user_node(test_user)

    @patch('flask.templating._render', return_value='Route To Manage System Page Works As Expected')
    def test_manage_systems_page_render(self, mocked):
        self.helper_create_user_node(test_user)
        self.helper_create_system_node(test_system_node)
        self.helper_make_admin_for_system(test_user['google_id'], test_system_node['system_uid'])
        with self.app as client:
            with client.session_transaction() as session:
                session['uid'] = test_user['sql_id']
            res = client.get('/social/manage/systems/' + str(system_uid))
            print(res.data)
            self.assertTrue(mocked.called, "Route To Manage System Page Failed: " + res.data)
        self.helper_leave_system(test_user['google_id'], test_system_node['system_uid'])
        self.helper_delete_system_node(test_system_node)
        self.helper_delete_user_node(test_user)

    @patch('flask.templating._render', return_value='Approve/Reject Systems Participant Works As Expected')
    def test_manage_systems_approve_reject_participant(self, mocked):
        self.helper_create_user_node(test_user)
        self.helper_create_user_node(test_user_system)
        self.helper_create_system_node(test_system_node)
        self.helper_make_admin_for_system(test_user['google_id'], test_system_node['system_uid'])
        self.helper_make_pending_participate_to_system(test_user_system['google_id'], test_system_node['system_uid'])
        with self.app as client:
            with client.session_transaction() as session:
                session['uid'] = test_user['sql_id']
            res = client.post('/social/systems/approve_reject_participant',
                              data=dict(system_uid=test_system_node['system_uid'],
                                        google_id=test_user_system['google_id'], submit="Approve"))
            self.assertFalse(mocked.called, "Approve Systems Participant Failed: " + res.data)
            self.helper_leave_system(test_user_system['google_id'], test_system_node['system_uid'])
            self.helper_make_pending_participate_to_system(test_user_system['google_id'],
                                                           test_system_node['system_uid'])
            res = client.post('/social/systems/approve_reject_participant',
                              data=dict(system_uid=system_uid, google_id=test_user_system['google_id'],
                                        submit="Reject"))
            self.assertFalse(mocked.called, "Reject Systems Participant Failed: " + res.data)
        self.helper_leave_system(test_user['google_id'], test_system_node['system_uid'])
        self.helper_delete_system_node(test_system_node)
        self.helper_delete_user_node(test_user_system)
        self.helper_delete_user_node(test_user)

    @patch('flask.templating._render', return_value='Participate/Subscribe/Leave System Works As Expected')
    def test_participate_subscribe_leave_system(self, mocked):
        self.helper_create_user_node(test_user)
        self.helper_create_system_node(test_system_node)
        with self.app as client:
            with client.session_transaction() as session:
                session['uid'] = test_user['sql_id']

            res = client.post('/social/systems/participate_subscribe_leave',
                              data=dict(system_uid=test_system_node['system_uid'],
                                        google_id=test_user['google_id'], submit="Subscribe"))
            self.assertFalse(mocked.called, "Subscribe For System Failed: " + res.data)
            self.helper_leave_system(test_user['google_id'], test_system_node['system_uid'])

            res = client.post('/social/systems/participate_subscribe_leave',
                              data=dict(system_uid=test_system_node['system_uid'],
                                        google_id=test_user['google_id'], submit="Participate"))
            self.assertFalse(mocked.called, "Participate For System Failed: " + res.data)
            self.helper_leave_system(test_user['google_id'], test_system_node['system_uid'])

            res = client.post('/social/systems/participate_subscribe_leave',
                              data=dict(system_uid=test_system_node['system_uid'],
                                        google_id=test_user['google_id'], submit="Leave"))
            self.assertFalse(mocked.called, "Leave System Failed: " + res.data)

        self.helper_delete_system_node(test_system_node)
        self.helper_delete_user_node(test_user)

    @patch('flask.templating._render', return_value='Delete or Make Admin / System Participant Works As Expected')
    def test_delete_system_participant_or_make_admin(self, mocked):
        self.helper_create_user_node(test_user)
        self.helper_create_user_node(test_user_system)
        self.helper_create_system_node(test_system_node)
        self.helper_make_admin_for_system(test_user['google_id'], test_system_node['system_uid'])
        self.helper_make_participate_to_system(test_user_system['google_id'], test_system_node['system_uid'])
        with self.app as client:
            with client.session_transaction() as session:
                session['uid'] = test_user['sql_id']

            res = client.post('/social/manage/systems/delete_system_participant_or_make_admin',
                              data=dict(system_uid=test_system_node['system_uid'],
                                        google_id=test_user_system['google_id'], submit="DeleteParticipant"))
            self.assertFalse(mocked.called, "Delete System Participant Failed: " + res.data)

            self.helper_make_participate_to_system(test_user_system['google_id'], test_system_node['system_uid'])
            res = client.post('/social/manage/systems/delete_system_participant_or_make_admin',
                              data=dict(system_uid=test_system_node['system_uid'],
                                        google_id=test_user_system['google_id'], submit="MakeSubscriber"))
            self.assertFalse(mocked.called, "Make System Participant as Subscriber Failed: " + res.data)

            self.helper_leave_system(test_user_system['google_id'], test_system_node['system_uid'])
            self.helper_make_participate_to_system(test_user_system['google_id'], test_system_node['system_uid'])
            res = client.post('/social/manage/systems/delete_system_participant_or_make_admin',
                              data=dict(system_uid=test_system_node['system_uid'],
                                        google_id=test_user_system['google_id'], submit="MakeAdmin"))
            self.assertFalse(mocked.called, "Make System Participant as Admin Failed: " + res.data)

        self.helper_leave_system(test_user_system['google_id'], test_system_node['system_uid'])
        self.helper_leave_system(test_user['google_id'], test_system_node['system_uid'])
        self.helper_delete_system_node(test_system_node)
        self.helper_delete_user_node(test_user_system)
        self.helper_delete_user_node(test_user)

    @patch('flask.templating._render', return_value='Delete Admin Of A System Works As Expected')
    def test_delete_system_admin(self, mocked):
        self.helper_create_user_node(test_user)
        self.helper_create_user_node(test_user_system)
        self.helper_create_system_node(test_system_node)
        self.helper_make_admin_for_system(test_user['google_id'], test_system_node['system_uid'])
        self.helper_make_admin_for_system(test_user_system['google_id'], test_system_node['system_uid'])
        with self.app as client:
            with client.session_transaction() as session:
                session['uid'] = test_user['sql_id']
            res = client.post('/social/manage/systems/delete_admin',
                              data=dict(system_uid=test_system_node['system_uid'],
                                        google_id=test_user_system['google_id'], submit="DeleteAdmin"))
            self.assertFalse(mocked.called, "Delete Admin Of A System Failed: " + res.data)
        self.helper_leave_system(test_user['google_id'], test_system_node['system_uid'])
        self.helper_delete_system_node(test_system_node)
        self.helper_delete_user_node(test_user_system)
        self.helper_delete_user_node(test_user)

    @patch('flask.templating._render', return_value='Delete or Make Admin / System Subscriber Works As Expected')
    def test_delete_system_subscriber_or_make_admin(self, mocked):
        self.helper_create_user_node(test_user)
        self.helper_create_user_node(test_user_system)
        self.helper_create_system_node(test_system_node)
        self.helper_make_admin_for_system(test_user['google_id'], test_system_node['system_uid'])
        self.helper_make_subscriber_to_system(test_user_system['google_id'], test_system_node['system_uid'])
        with self.app as client:
            with client.session_transaction() as session:
                session['uid'] = test_user['sql_id']

            res = client.post('/social/manage/systems/delete_system_subscriber_or_make_admin',
                              data=dict(system_uid=test_system_node['system_uid'],
                                        google_id=test_user_system['google_id'], submit="DeleteSubscriber"))
            self.assertFalse(mocked.called, "Delete System Subscriber Failed: " + res.data)

            self.helper_make_subscriber_to_system(test_user_system['google_id'], test_system_node['system_uid'])
            res = client.post('/social/manage/systems/delete_system_subscriber_or_make_admin',
                              data=dict(system_uid=test_system_node['system_uid'],
                                        google_id=test_user_system['google_id'], submit="MakeParticipant"))
            self.assertFalse(mocked.called, "Make System Subscriber as Participant Failed: " + res.data)

            self.helper_leave_system(test_user_system['google_id'], test_system_node['system_uid'])
            self.helper_make_subscriber_to_system(test_user_system['google_id'], test_system_node['system_uid'])
            res = client.post('/social/manage/systems/delete_system_subscriber_or_make_admin',
                              data=dict(system_uid=test_system_node['system_uid'],
                                        google_id=test_user_system['google_id'], submit="MakeAdmin"))
            self.assertFalse(mocked.called, "Make System Subscriber as Admin Failed: " + res.data)

        self.helper_leave_system(test_user_system['google_id'], test_system_node['system_uid'])
        self.helper_leave_system(test_user['google_id'], test_system_node['system_uid'])
        self.helper_delete_system_node(test_system_node)
        self.helper_delete_user_node(test_user_system)
        self.helper_delete_user_node(test_user)

    # --------------------------------------------------------------------------------------
    # Helper Functions For Unit Test
    # --------------------------------------------------------------------------------------

    # Helper Function To Create User Node In Neo4J Database
    def helper_create_user_node(self, user_node_to_create):
        try:
            # Same User Node If Exists Is Removed
            self.helper_delete_user_node(user_node_to_create)
            graph.create(user_node_to_create)
        except Exception as ex:
            print "Exception At helper_create_user_node: " + str(ex.message)

    # Helper Function To Delete User Node In Neo4J Database
    def helper_delete_user_node(self, user_node_to_delete):
        try:
            delete_user_query = """
                MATCH (u:User)
                WHERE u.sql_id = {sql_id}
                DETACH DELETE u
            """
            delete_user_status = graph.cypher.execute(delete_user_query, sql_id=user_node_to_delete["sql_id"])
        except Exception as ex:
            print "Exception At helper_delete_user_node: " + str(ex.message)

    # Helper Function To Create Group Node In Neo4J Database
    def helper_create_group_node(self, group_node_to_create):
        try:
            # Same Group Node If Exists Is Removed
            self.helper_delete_group_node(group_node_to_create)
            graph.create(group_node_to_create)
        except Exception as ex:
            print "Exception At helper_create_group_node: " + str(ex.message)

    # Helper Function To Delete User Node In Neo4J Database
    def helper_delete_group_node(self, group_node_to_delete):
        try:
            delete_group_query = """
                MATCH (g:Group)
                WHERE g.group_uid = {group_uid}
                DETACH DELETE g
            """
            delete_group_status = graph.cypher.execute(delete_group_query, group_uid=group_node_to_delete["group_uid"])
        except Exception as ex:
            print "Exception At helper_delete_group_node: " + str(ex.message)

    # Helper function for creating friend relation
    def helper_make_friend(self,google_id):
        try:
            User(test_user['sql_id']).accept_friend_request(google_id)
        except Exception as ex:
            print "Exception At helper_make_friends: " + str(ex.message)

    def helper_delete_friend(self,google_id):
        try:
            User(test_user['sql_id']).delete_friend(google_id)
        except Exception as ex:
            print "Exception At helper_delete_friend: " + str(ex.message)



    # Helper Function To Make An User Admin For A Group Node In Neo4J Database
    def helper_make_admin_for_group(self, google_id, group_uid):
        try:
            Group().make_admin_for_group(google_id, group_uid)
        except Exception as ex:
            print "Exception At helper_make_admin_for_group: " + str(ex.message)

    # Helper Function To Make An User Pending Member For A Group Node In Neo4J Database
    def helper_make_pending_member_to_group(self, google_id, group_uid):
        try:
            Group().join_group_pending(google_id, group_uid)
        except Exception as ex:
            print "Exception At helper_make_pending_member_to_group: " + str(ex.message)

    # Helper Function To Make An User Member For A Group Node In Neo4J Database
    def helper_make_member_to_group(self, google_id, group_uid):
        try:
            Group().join_group(google_id, group_uid)
        except Exception as ex:
            print "Exception At helper_make_member_to_group: " + str(ex.message)

    # Helper Function To Delete The User Relationship With The Group Node In Neo4J Database
    def helper_leave_group(self, google_id, group_uid):
        try:
            Group().leave_group(google_id, group_uid)
        except Exception as ex:
            print "Exception At helper_leave_group: " + str(ex.message)

    # Helper Function To Create System Node In Neo4J Database
    def helper_create_system_node(self, system_node_to_create):
        try:
            # Same System Node If Exists Is Removed
            self.helper_delete_system_node(system_node_to_create)
            graph.create(system_node_to_create)
        except Exception as ex:
            print "Exception At helper_create_system_node: " + str(ex.message)

    # Helper Function To Make An User Admin For A System Node In Neo4J Database
    def helper_make_admin_for_system(self, google_id, system_uid):
        try:
            System().make_admin_for_system(google_id, system_uid)
        except Exception as ex:
            print "Exception At helper_make_admin_for_system: " + str(ex.message)

    # Helper Function To Make An User Pending Participant For A System Node In Neo4J Database
    def helper_make_pending_participate_to_system(self, google_id, system_uid):
        try:
            System().pending_participate_to_system(google_id, system_uid)
        except Exception as ex:
            print "Exception At helper_make_pending_participate_to_system: " + str(ex.message)

    # Helper Function To Make An User Participant For A System Node In Neo4J Database
    def helper_make_participate_to_system(self, google_id, system_uid):
        try:
            System().approve_system_participant(google_id, system_uid)
        except Exception as ex:
            print "Exception At helper_make_participate_to_system: " + str(ex.message)

    # Helper Function To Make An User Subscriber For A System Node In Neo4J Database
    def helper_make_subscriber_to_system(self, google_id, system_uid):
        try:
            System().subscribe_to_system(google_id, system_uid)
        except Exception as ex:
            print "Exception At helper_make_subscriber_to_system: " + str(ex.message)

    # Helper Function To Delete The User Relationship With The System Node In Neo4J Database
    def helper_leave_system(self, google_id, system_uid):
        try:
            System().leave_system(google_id, system_uid)
        except Exception as ex:
            print "Exception At helper_leave_system: " + str(ex.message)

    # Helper Function To Delete System Node In Neo4J Database
    def helper_delete_system_node(self, system_node_to_delete):
        try:
            delete_system_query = """
                MATCH (s:System)
                WHERE s.system_uid = {system_uid}
                DETACH DELETE s
            """
            delete_system_status = graph.cypher.execute(delete_system_query,
                                                        system_uid=system_node_to_delete['system_uid'])
        except Exception as ex:
            print "Exception At helper_delete_system_node: " + str(ex.message)

    # --------------------------------------------------------------------------------------

    if __name__ == '__main__':
        unittest.main()
