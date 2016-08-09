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
        global post_id
        post_id = 1
        global post_system_id
        post_system_id = 2
        global post_group_id
        post_group_id = 3
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
        global test_post_node
        test_post_node = Node(
            "Post",
            id=str(post_id),
            text="This is a test post",
            privacy="Public",
            userid=sql_id,
            creation_time=1461345863010,
            modified_time=1461345863010,
            date=1461345863010,
            link="None",
            link_title="None",
            link_img="None",
            link_description="None"
        )
        global test_comment_id
        test_comment_id = 1
        global test_comment
        test_comment = Node(
            "Comment",
            id=str(test_comment_id),
            content="This is a new comment",
            user_sql_id=sql_id,
            user_display_name="Test User For System",
            creation_time=1461345863010,
            modified_time=1461345863010
        )
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
        global test_system_post_node
        test_system_post_node = Node(
            "SystemPost",
            id=str(post_system_id),
            text="This is a test system post",
            privacy="Public",
            userid=sql_id,
            creation_time=1461345863010,
            modified_time=1461345863010,
            date=1461345863010,
            link="None",
            link_title="None",
            link_img="None",
            link_description="None"
        )
        global test_system_comment_id
        test_system_comment_id = 1
        global test_system_comment
        test_system_comment = Node(
            "SystemComment",
            id=str(test_system_comment_id),
            content="This is a new system comment",
            user_sql_id=sql_id,
            user_display_name="Test User For System",
            creation_time=1461345863010,
            modified_time=1461345863010
        )
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
        global test_group_post_node
        test_group_post_node = Node(
            "GroupPost",
            id=str(post_group_id),
            text="This is a test group post",
            privacy="Public",
            userid=sql_id,
            creation_time=1461345863010,
            modified_time=1461345863010,
            date=1461345863010,
            link="None",
            link_title="None",
            link_img="None",
            link_description="None"
        )
        global test_group_comment_id
        test_group_comment_id = 1
        global test_group_comment
        test_group_comment = Node(
            "GroupComment",
            id=str(test_group_comment_id),
            content="This is a new group comment",
            user_sql_id=sql_id,
            user_display_name="Test User For System",
            creation_time=1461345863010,
            modified_time=1461345863010
        )
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

        # --------------------------------------------------------------------------------------
        # Dummy User For Timeline Page
        # --------------------------------------------------------------------------------------
        global sql_id_user_timeline
        sql_id_user_timeline = 46250
        global google_id_user_timeline
        google_id_user_timeline = "608205396037595043178"
        global test_user_timeline
        test_user_timeline = Node("User",
                                  sql_id=sql_id_user_timeline, google_id=google_id_user_timeline,
                                  givenName="Test User For Timeline",
                                  familyName="Test User For Timeline",
                                  displayName="Test User For Timeline",
                                  email="ISBTestUser@gmail.com", gender="male", dob="1989-03-19",
                                  image_url="https://www.gstatic.com/webp/gallery3/1.png",
                                  user_type="subscriber", organization="Northeastern University",
                                  creation_time=1461345863010,
                                  modified_time=1461345863010, status=0)
        # --------------------------------------------------------------------------------------

        global graph
        graph = models.get_graph_connection_uri()

    # --------------------------------------------------------------------------------------
    # Login / Logout Page Tests
    # --------------------------------------------------------------------------------------
    @patch('flask.templating._render', return_value='Logout Works As Expected')
    def test_logout(self, mocked):
        self.helper_create_user_node(test_user)
        with self.app as client:
            with client.session_transaction() as session:
                session['uid'] = test_user['sql_id']
            res = client.get('/social/logout')
            self.assertFalse(mocked.called, "Logout Failed: " + res.data)
        self.helper_delete_user_node(test_user)

    # --------------------------------------------------------------------------------------
    # Home Page Tests
    # --------------------------------------------------------------------------------------

    @patch('flask.templating._render', return_value='Route To Home Page Render Works As Expected')
    def test_home_page_render(self, mocked):
        self.helper_create_user_node(test_user)
        with self.app as client:
            with client.session_transaction() as session:
                session['uid'] = test_user['sql_id']
            res = client.get('/social/index')
            print res.data
            self.assertTrue(mocked.called, "Route To Home Page Render Failed: " + res.data)
        self.helper_delete_user_node(test_user)

    @patch('flask.templating._render', return_value='Add home post Works As Expected')
    def test_add_home_post(self, mocked):
        self.helper_create_user_node(test_user)
        with self.app as client:
            with client.session_transaction() as session:
                session['uid'] = test_user['sql_id']
            res = client.post('/social/add_post',
                              data=dict(google_id=test_user['google_id'], privacy="public",
                                        text="This is a test post",
                                        link="None", link_title="None", link_img="None", link_description="None",
                                        page_type="home"))
            self.assertFalse(mocked.called, "Add home post Failed: " + res.data)
        self.helper_delete_user_node(test_user)
        self.helper_delete_user_posts()

    @patch('flask.templating._render', return_value='Delete home post Works As Expected')
    def test_delete_home_post(self, mocked):
        self.helper_create_user_node(test_user)
        self.helper_create_post_node(test_post_node)
        with self.app as client:
            with client.session_transaction() as session:
                session['uid'] = test_user['sql_id']
            res = client.post('/social/delete_post',
                              data=dict(postid=post_id))
            # print(res.data)
            self.assertFalse(mocked.called, "Delete home post Failed: " + res.data)
        self.helper_delete_post_node(post_id)
        self.helper_delete_user_node(test_user)

    @patch('flask.templating._render', return_value='Edit home post Works As Expected')
    def test_edit_home_post(self, mocked):
        self.helper_create_user_node(test_user)
        self.helper_create_post_node(test_post_node)
        with self.app as client:
            with client.session_transaction() as session:
                session['uid'] = test_user['sql_id']
            res = client.post('/social/edit_post',
                              data=dict(postid=post_id, editedpost="This is an edited post"))
            # print(res.data)
            self.assertFalse(mocked.called, "Edit home post Failed: " + res.data)
        self.helper_delete_post_node(test_post_node['id'])
        self.helper_delete_user_node(test_user)

    @patch('flask.templating._render', return_value='Add home comment Works As Expected')
    def test_add_home_comment(self, mocked):
        self.helper_create_user_node(test_user)
        self.helper_create_post_node(test_post_node)
        with self.app as client:
            with client.session_transaction() as session:
                session['uid'] = test_user['sql_id']
            res = client.post('/social/add_comment',
                              data=dict(postid=int(test_post_node['id']),
                                        newcomment="This is a test comment"))
            # print(res.data)
            self.assertFalse(mocked.called, "Add home comment Failed: " + res.data)
        self.helper_delete_post_node(test_post_node['id'])
        self.helper_delete_user_node(test_user)
        self.helper_delete_comment()

    @patch('flask.templating._render', return_value='Add home comment Works As Expected')
    def test_no_comment_add_home_comment(self, mocked):
        self.helper_create_user_node(test_user)
        self.helper_create_post_node(test_post_node)
        with self.app as client:
            with client.session_transaction() as session:
                session['uid'] = test_user['sql_id']
            res = client.post('/social/add_comment',
                              data=dict(postid=int(test_post_node['id']),
                                        newcomment=""))
            # print(res.data)
            self.assertFalse(mocked.called, "Add home comment Failed: " + res.data)
        self.helper_delete_post_node(test_post_node['id'])
        self.helper_delete_user_node(test_user)
        self.helper_delete_comment()

    @patch('flask.templating._render', return_value='Add home comment Works As Expected')
    def test_no_postid_add_home_comment(self, mocked):
        self.helper_create_user_node(test_user)
        self.helper_create_post_node(test_post_node)
        with self.app as client:
            with client.session_transaction() as session:
                session['uid'] = test_user['sql_id']
            res = client.post('/social/add_comment',
                              data=dict(postid="",
                                        newcomment="asd"))
            # print(res.data)
            self.assertFalse(mocked.called, "Add home comment Failed: " + res.data)
        self.helper_delete_post_node(test_post_node['id'])
        self.helper_delete_user_node(test_user)
        self.helper_delete_comment()

    @patch('flask.templating._render', return_value='Like home post Works As Expected')
    def test_like_home_post(self, mocked):
        self.helper_create_user_node(test_user)
        self.helper_create_post_node(test_post_node)
        with self.app as client:
            with client.session_transaction() as session:
                session['uid'] = test_user['sql_id']
            res = client.post('/social/like_or_unlike_post',
                              data=dict(postid=int(test_post_node['id']),
                                        submit="likePost"))
            # print(res.data)
            self.assertFalse(mocked.called, "Like home post Failed: " + res.data)
        self.helper_delete_post_node(test_post_node['id'])
        self.helper_delete_user_node(test_user)

    @patch('flask.templating._render', return_value='UnLike home post Works As Expected')
    def test_unlike_home_post(self, mocked):
        self.helper_create_user_node(test_user)
        self.helper_create_post_node(test_post_node)
        with self.app as client:
            with client.session_transaction() as session:
                session['uid'] = test_user['sql_id']
            res = client.post('/social/like_or_unlike_post',
                              data=dict(postid=int(test_post_node['id']),
                                        submit="unlikePost"))
            # print(res.data)
            self.assertFalse(mocked.called, "UnLike post Failed: " + res.data)
        self.helper_delete_post_node(test_post_node['id'])
        self.helper_delete_user_node(test_user)

    @patch('flask.templating._render', return_value='Edit home comment Works As Expected')
    def test_edit_home_comment(self, mocked):
        self.helper_create_user_node(test_user)
        self.helper_create_post_node(test_post_node)
        self.helper_create_comment_node(test_comment)
        with self.app as client:
            with client.session_transaction() as session:
                session['uid'] = test_user['sql_id']
            res = client.post('/social/edit_or_delete_comment',
                              data=dict(commentid=test_comment_id,
                                        editedcomment="This is test edited comment",
                                        submit="editComment"))
            # print(res.data)
            self.assertFalse(mocked.called, "Edit home comment Failed: " + res.data)
        self.helper_delete_post_node(test_post_node['id'])
        self.helper_delete_comment_node(test_comment['id'])
        self.helper_delete_user_node(test_user)

    @patch('flask.templating._render', return_value='Delete home comment Works As Expected')
    def test_delete_home_comment(self, mocked):
        self.helper_create_user_node(test_user)
        self.helper_create_post_node(test_post_node)
        self.helper_create_comment_node(test_comment)
        with self.app as client:
            with client.session_transaction() as session:
                session['uid'] = test_user['sql_id']
            res = client.post('/social/edit_or_delete_comment',
                              data=dict(commentid=test_comment_id,
                                        submit="deleteComment"))
            # print(res.data)
            self.assertFalse(mocked.called, "Delete home comment Failed: " + res.data)
        self.helper_delete_post_node(test_post_node['id'])
        self.helper_delete_comment_node(test_comment['id'])
        self.helper_delete_user_node(test_user)

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

    @patch('flask.templating._render', return_value='Route To Friends Page Works As Expected')
    def test_friends_no_user(self, mocked):
        self.helper_create_user_node(test_user)
        with self.app as client:
            with client.session_transaction() as session:
                session['uid'] = ""
        res = client.get('/social/friends')
        print(res.data)
        self.assertTrue(mocked.called, "Route To Friends Page Passed: " + res.data)
        self.helper_delete_user_node(test_user)

    @patch('flask.templating._render', return_value='Accept Friend Request Works As Expected')
    def test_accept_friend_request(self, mocked):
        self.helper_create_user_node(test_user)
        self.helper_create_user_node(test_user_friend)
        self.helper_send_friend_request(test_user_friend['sql_id'])
        with self.app as client:
            with client.session_transaction() as session:
                session['uid'] = test_user['sql_id']
        res = client.post('/social/accept_friend_request/' + str(test_user_friend['sql_id']))
        self.assertFalse(mocked.called, "Accept Friend Request Failed: " + res.data)
        self.helper_delete_friend(test_user_friend['sql_id'])
        self.helper_delete_user_node(test_user_friend)
        self.helper_delete_user_node(test_user)

    @patch('flask.templating._render', return_value='Delete Friend Request Works As Expected')
    def test_decline_friend_request(self, mocked):
        self.helper_create_user_node(test_user)
        self.helper_create_user_node(test_user_friend)
        self.helper_make_friend(test_user_friend['sql_id'])
        with self.app as client:
            with client.session_transaction() as session:
                session['uid'] = test_user['sql_id']
        res = client.post('/social/decline_friend_request/' + str(test_user_friend['sql_id']))
        self.assertFalse(mocked.called, "Delete Friend Request Failed: " + res.data)
        self.helper_delete_user_node(test_user_friend)
        self.helper_delete_user_node(test_user)

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

    @patch('flask.templating._render', return_value='View pending friend request works as expected')
    def test_view_pending_nosql_friend_request(self, mocked):
        graph.create(test_user)
        with self.app as client:
            with client.session_transaction() as session:
                session['uid'] = ""
            res = client.get('/social/pendingRequest')
            print(res.data)
            self.assertTrue(mocked.called, "View_pending_friend_request Passed: " + res.data)
        self.helper_delete_user_node(test_user)

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

    @patch('flask.templating._render', return_value='Recommended friend test works as expected')
    def test_reco_nouser_friend_request(self, mocked):
        self.helper_create_user_node(test_user)
        with self.app as client:
            with client.session_transaction() as session:
                session['uid'] = ""
            res = client.get('/social/recofriends')
            print(res.data)
            self.assertTrue(mocked.called, "test_reco_friend_request Passed: " + res.data)
        self.helper_delete_user_node(test_user)

    """
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
    """

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

    @patch('flask.templating._render', return_value='Search Friends work as expected')
    def test_search_friend_nouser(self, mocked):
        self.helper_create_user_node(test_user)
        with self.app as client:
            with client.session_transaction() as session:
                session['uid'] = ""
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
            res = client.post('/social/block_friend/' + str(test_user_friend['sql_id']))
            self.assertFalse(mocked.called, "Block Friends passed: " + res.data)
        self.helper_delete_friend(test_user_friend['sql_id'])
        self.helper_delete_user_node(test_user_friend)
        self.helper_delete_user_node(test_user)

    @patch('flask.templating._render', return_value='Send friend request Works')
    def test_send_friend_request(self, mocked):
        self.helper_create_user_node(test_user)
        self.helper_create_user_node(test_user_friend)
        self.helper_make_friend(test_user_friend['sql_id'])
        with self.app as client:
            with client.session_transaction() as session:
                session['uid'] = test_user['sql_id']
            res = client.post('/social/send_friend_request/' + str(test_user_friend['sql_id']))
            self.assertFalse(mocked.called, "send_friend_request passed: " + res.data)
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
            res = client.post('/social/block_friend/' + str(test_user_friend['sql_id']))
            res2 = client.post('/social/unblock_friend/' + str(test_user_friend['sql_id']))
            self.assertFalse(mocked.called, "Block Friends passed: " + res.data)
        self.helper_delete_friend(test_user_friend['sql_id'])
        self.helper_delete_user_node(test_user_friend)
        self.helper_delete_user_node(test_user)

    @patch('flask.templating._render', return_value='Delete Friend Works')
    def test_delete_friend(self, mocked):
        self.helper_create_user_node(test_user)
        self.helper_create_user_node(test_user_friend)
        self.helper_make_friend(test_user_friend['sql_id'])
        with self.app as client:
            with client.session_transaction() as session:
                session['uid'] = test_user['sql_id']
            res = client.post('/social/delete_friend/' + str(test_user_friend['sql_id']))
            self.assertFalse(mocked.called, "Delete Friends passed: " + res.data)
        self.helper_delete_user_node(test_user_friend)
        self.helper_delete_user_node(test_user)

    @patch('flask.templating._render', return_value='Get Friends JSON For Search Friends Works As Expected')
    def test_get_friends(self, mocked):
        self.helper_create_user_node(test_user)
        with self.app as client:
            with client.session_transaction() as session:
                session['uid'] = test_user['sql_id']
            res = client.get('/social/getfriends')
            self.assertFalse(mocked.called, "Get Friends JSON For Search Friends Failed: " + res.data)
        self.helper_delete_user_node(test_user)

    # --------------------------------------------------------------------------------------
    # Profile Page tests
    # --------------------------------------------------------------------------------------
    @patch('flask.templating._render', return_value='Add profile post Works As Expected')
    def test_add_profile_post(self, mocked):
        self.helper_create_user_node(test_user)
        with self.app as client:
            with client.session_transaction() as session:
                session['uid'] = test_user['sql_id']
            res = client.post('/social/add_post',
                              data=dict(google_id=test_user['google_id'], privacy="public",
                                        text="This is a test post",
                                        link="None", link_title="None", link_img="None", link_description="None",
                                        page_type="profile"))
            self.assertFalse(mocked.called, "Add profile post Failed: " + res.data)
        self.helper_delete_user_node(test_user)
        self.helper_delete_user_posts()

    # --------------------------------------------------------------------------------------
    # Edit Profile related Tests
    # --------------------------------------------------------------------------------------

    @patch('flask.templating._render', return_value='Edit Profile Page Render Works As Expected')
    def test_editprofile_page_render(self, mocked):
        self.helper_create_user_node(test_user)
        with self.app as client:
            with client.session_transaction() as session:
                session['uid'] = test_user['sql_id']
            res = client.get('/social/editprofile')
            print(res.data)
            self.assertTrue(mocked.called, "Edit Profile Page Render Failed: " + res.data)
        self.helper_delete_user_node(test_user)

    @patch('flask.templating._render', return_value='Update Profile Functionality Works As Expected')
    def test_update_profile(self, mocked):
        self.helper_create_user_node(test_user)
        with self.app as client:
            with client.session_transaction() as session:
                session['uid'] = test_user['sql_id']
            res = client.post('/social/updateprofile',
                              data=dict(givenName="Chandler", familyName="Bing", displayName="Chandler", gender="Male",
                                        organization="Northeastern", user_type="participant", dob="1989-12-20"))
            print(res)
            self.assertTrue(mocked.called, "Route To Home Page Failed: " + res.data)
        self.helper_delete_user_node(test_user)

    @patch('flask.templating._render', return_value='Update Profile Functionality Works As Expected')
    def test_update_no_sql_profile(self, mocked):
        self.helper_create_user_node(test_user)
        with self.app as client:
            with client.session_transaction() as session:
                session['uid'] = ""
            res = client.post('/social/updateprofile',
                              data=dict(givenName="Chandler", familyName="Bing", displayName="Chandler", gender="Male",
                                        organization="Northeastern", user_type="participant", dob="1989-12-20"))
            print(res)
            self.assertTrue(mocked.called, "Route To Home Page Failed: " + res.data)
        self.helper_delete_user_node(test_user)

    # --------------------------------------------------------------------------------------
    # Timeline related Tests
    # --------------------------------------------------------------------------------------

    """
    # TimeLine Page Render Requires Google Access Token Which Obtained At RunTime When The User Logs In. Cannot Be Mocked.
    @patch('flask.templating._render', return_value='Timeline Page Render Works As Expected')
    def test_timeline_page_render(self, mocked):
        self.helper_create_user_node(test_user)
        self.helper_create_user_node(test_user_timeline)
        with self.app as client:
            with client.session_transaction() as session:
                session['uid'] = test_user['sql_id']
            res = client.get('/social/profile/' + str(test_user_timeline['google_id']))
            print(res.data)
            self.assertTrue(mocked.called, "Route To Home Page Failed: " + res.data)
        self.helper_delete_user_node(test_user_timeline)
        self.helper_delete_user_node(test_user)
    """

    @patch('flask.templating._render', return_value='Delete Friend on Timeline Page Works As Expected')
    def test_timeline_delete_friend(self, mocked):
        self.helper_create_user_node(test_user)
        self.helper_create_user_node(test_user_timeline)
        self.helper_make_friend(test_user_timeline['sql_id'])
        with self.app as client:
            with client.session_transaction() as session:
                session['uid'] = test_user['sql_id']
            res = client.get('/social/delete_friend_timeline/' +
                             str(test_user_timeline['sql_id']) + "?next=/profile/" + str(test_user['google_id']))
            self.assertFalse(mocked.called, "Route To Home Page Failed: " + res.data)
        self.helper_delete_user_node(test_user_timeline)
        self.helper_delete_user_node(test_user)

    # -- Review
    """
    @patch('flask.templating._render', return_value='Make Post on Timeline Page Works As Expected')
    def test_timeline_post(self, mocked):
        self.helper_create_user_node(test_user)
        self.helper_create_user_node(test_user_timeline)
        self.helper_make_friend(test_user_timeline['sql_id'])
        with self.app as client:
            with client.session_transaction() as session:
                session['uid'] = test_user['sql_id']
            res = client.post('/social/add_profile_post',
                              data=dict(str(test_user['google_id']), "profile",
                                        "https://pf1010.systemsbiology.net/contact"))
            self.assertFalse(mocked.called, "Make Post on Timeline Page Failed: " + res.data)
        self.helper_delete_user_node(test_user_timeline)
        self.helper_delete_user_node(test_user)
    """

    # --------------------------------------------------------------------------------------
    # Groups Page Tests
    # --------------------------------------------------------------------------------------

    @patch('flask.templating._render', return_value='Add group post Works As Expected')
    def test_add_group_post(self, mocked):
        self.helper_create_user_node(test_user)
        self.helper_create_group_node(test_group_node)
        with self.app as client:
            with client.session_transaction() as session:
                session['uid'] = test_user['sql_id']
            res = client.post('/social/groups/add_group_post',
                              data=dict(group_uid=group_uid, privacy="public", text="This is a test group post",
                                        link="None", link_title="None", link_img="None", link_description="None"))
            self.assertFalse(mocked.called, "Add group post Failed: " + res.data)
        self.helper_delete_group_node(test_group_node)
        self.helper_delete_user_node(test_user)
        self.helper_delete_group_posts()

    @patch('flask.templating._render', return_value='Delete group post Works As Expected')
    def test_delete_group_post(self, mocked):
        self.helper_create_user_node(test_user)
        self.helper_create_group_node(test_group_node)
        self.helper_create_group_post_node(test_group_post_node)
        with self.app as client:
            with client.session_transaction() as session:
                session['uid'] = test_user['sql_id']
            res = client.post('/social/delete_group_post',
                              data=dict(group_uid=group_uid, postid=post_group_id))
            # print(res.data)
            self.assertFalse(mocked.called, "Delete group post Failed: " + res.data)
        self.helper_delete_group_node(test_group_node)
        self.helper_delete_group_post_node(test_group_post_node['id'])
        self.helper_delete_user_node(test_user)

    @patch('flask.templating._render', return_value='Edit group post Works As Expected')
    def test_edit_group_post(self, mocked):
        self.helper_create_user_node(test_user)
        self.helper_create_group_node(test_group_node)
        self.helper_create_group_post_node(test_group_post_node)
        with self.app as client:
            with client.session_transaction() as session:
                session['uid'] = test_user['sql_id']
            res = client.post('/social/edit_group_post',
                              data=dict(group_uid=group_uid, postid=post_group_id, editedpost="This is an edited post"))
            # print(res.data)
            self.assertFalse(mocked.called, "Edit group post Failed: " + res.data)
        self.helper_delete_group_post_node(post_group_id)
        self.helper_delete_group_node(test_group_node)
        self.helper_delete_user_node(test_user)

    @patch('flask.templating._render', return_value='Add group comment Works As Expected')
    def test_add_group_comment(self, mocked):
        self.helper_create_user_node(test_user)
        self.helper_create_group_node(test_group_node)
        self.helper_create_group_post_node(test_group_post_node)
        with self.app as client:
            with client.session_transaction() as session:
                session['uid'] = test_user['sql_id']
            res = client.post('/social/add_group_comment',
                              data=dict(group_uid=group_uid, postid=int(test_group_post_node['id']),
                                        newcomment="This is a new group comment"))
            # print(res.data)
            self.assertFalse(mocked.called, "Add group comment Failed: " + res.data)
        self.helper_delete_group_post_node(test_group_post_node['id'])
        self.helper_delete_group_node(test_group_node)
        self.helper_delete_user_node(test_user)
        self.helper_delete_group_comment()

    @patch('flask.templating._render', return_value='Like group post Works As Expected')
    def test_like_group_post(self, mocked):
        self.helper_create_user_node(test_user)
        self.helper_create_group_node(test_group_node)
        self.helper_create_group_post_node(test_group_post_node)
        with self.app as client:
            with client.session_transaction() as session:
                session['uid'] = test_user['sql_id']
            res = client.post('/social/like_or_unlike_group_post',
                              data=dict(group_uid=group_uid, postid=int(test_group_post_node['id']),
                                        submit="likePost"))
            # print(res.data)
            self.assertFalse(mocked.called, "Like group post Failed: " + res.data)
        self.helper_delete_group_post_node(test_group_post_node['id'])
        self.helper_delete_group_node(test_group_node)
        self.helper_delete_user_node(test_user)

    @patch('flask.templating._render', return_value='UnLike group post Works As Expected')
    def test_unlike_group_post(self, mocked):
        self.helper_create_user_node(test_user)
        self.helper_create_group_node(test_group_node)
        self.helper_create_group_post_node(test_group_post_node)
        with self.app as client:
            with client.session_transaction() as session:
                session['uid'] = test_user['sql_id']
            res = client.post('/social/like_or_unlike_group_post',
                              data=dict(group_uid=group_uid, postid=int(test_group_post_node['id']),
                                        submit="unlikePost"))
            # print(res.data)
            self.assertFalse(mocked.called, "UnLike group post Failed: " + res.data)
        self.helper_delete_group_post_node(test_group_post_node['id'])
        self.helper_delete_group_node(test_group_node)
        self.helper_delete_user_node(test_user)

    @patch('flask.templating._render', return_value='Edit group comment Works As Expected')
    def test_edit_group_comment(self, mocked):
        self.helper_create_user_node(test_user)
        self.helper_create_group_node(test_group_node)
        self.helper_create_group_post_node(test_group_post_node)
        self.helper_create_group_comment_node(test_group_comment)
        with self.app as client:
            with client.session_transaction() as session:
                session['uid'] = test_user['sql_id']
            res = client.post('/social/edit_or_delete_group_comment',
                              data=dict(group_uid=group_uid, commentid=test_group_comment_id,
                                        editedcomment="This is test edited comment",
                                        submit="editComment"))
            # print(res.data)
            self.assertFalse(mocked.called, "Edit group comment Failed: " + res.data)
        self.helper_delete_group_post_node(test_group_post_node['id'])
        self.helper_delete_group_comment_node(test_group_comment['id'])
        self.helper_delete_group_node(test_group_node)
        self.helper_delete_user_node(test_user)

    @patch('flask.templating._render', return_value='Delete group comment Works As Expected')
    def test_delete_group_comment(self, mocked):
        self.helper_create_user_node(test_user)
        self.helper_create_group_node(test_group_node)
        self.helper_create_group_post_node(test_group_post_node)
        self.helper_create_group_comment_node(test_group_comment)
        with self.app as client:
            with client.session_transaction() as session:
                session['uid'] = test_user['sql_id']
            res = client.post('/social/edit_or_delete_group_comment',
                              data=dict(group_uid=group_uid, commentid=test_group_comment_id,
                                        submit="deleteComment"))
            # print(res.data)
            self.assertFalse(mocked.called, "Delete group comment Failed: " + res.data)
        self.helper_delete_group_post_node(test_group_post_node['id'])
        self.helper_delete_group_node(test_group_node)
        self.helper_delete_user_node(test_user)

    @patch('flask.templating._render', return_value='Create Groups Page Render Works As Expected')
    def test_create_groups_page_render(self, mocked):
        self.helper_create_user_node(test_user)
        with self.app as client:
            with client.session_transaction() as session:
                session['uid'] = test_user['sql_id']
            res = client.get('/social/groups/')
            print(res.data)
            self.assertTrue(mocked.called, "Create Groups Page Render failed: " + res.data)
        self.helper_delete_user_node(test_user)

    @patch('flask.templating._render', return_value='Create Groups Page Render Works As Expected')
    def test_no_user_create_groups_page_render(self, mocked):
        self.helper_create_user_node(test_user)
        with self.app as client:
            with client.session_transaction() as session:
                session['uid'] = ""
            res = client.get('/social/groups/')
            print(res.data)
            self.assertTrue(mocked.called, "Create Groups Page Render failed: " + res.data)
        self.helper_delete_user_node(test_user)

    @patch('flask.templating._render', return_value='My Groups Page Render Works As Expected')
    def test_my_group_page_render(self, mocked):
        self.helper_create_user_node(test_user)
        with self.app as client:
            with client.session_transaction() as session:
                session['uid'] = test_user['sql_id']
            res = client.get('/social/groups/self')
            print(res.data)
            self.assertTrue(mocked.called, "My Groups Page Render Failed: " + res.data)
        self.helper_delete_user_node(test_user)

    @patch('flask.templating._render', return_value='My Groups Page Render Works As Expected')
    def test_no_user_my_group_page_render(self, mocked):
        self.helper_create_user_node(test_user)
        with self.app as client:
            with client.session_transaction() as session:
                session['uid'] = ""
            res = client.get('/social/groups/self')
            print(res.data)
            self.assertTrue(mocked.called, "My Groups Page Render Failed: " + res.data)
        self.helper_delete_user_node(test_user)

    @patch('flask.templating._render', return_value='Search Groups Page Render Works As Expected')
    def test_search_group_page_render(self, mocked):
        self.helper_create_user_node(test_user)
        with self.app as client:
            with client.session_transaction() as session:
                session['uid'] = test_user['sql_id']
            res = client.get('/social/groups/search')
            print(res.data)
            self.assertTrue(mocked.called, "Search Groups Page Render Failed: " + res.data)
        self.helper_delete_user_node(test_user)

    @patch('flask.templating._render', return_value='Search Groups Page Render Works As Expected')
    def test_no_user_search_group_page_render(self, mocked):
        self.helper_create_user_node(test_user)
        with self.app as client:
            with client.session_transaction() as session:
                session['uid'] = ""
            res = client.get('/social/groups/search')
            print(res.data)
            self.assertTrue(mocked.called, "Search Groups Page Render Failed: " + res.data)
        self.helper_delete_user_node(test_user)

    @patch('flask.templating._render', return_value='Recommended Groups Page Render Works As Expected')
    def test_recommended_group_page_render(self, mocked):
        self.helper_create_user_node(test_user)
        with self.app as client:
            with client.session_transaction() as session:
                session['uid'] = test_user['sql_id']
            res = client.get('/social/groups/recommended')
            print(res.data)
            self.assertTrue(mocked.called, "Recommended Groups Page Render Failed: " + res.data)
        self.helper_delete_user_node(test_user)

    @patch('flask.templating._render', return_value='Recommended Groups Page Render Works As Expected')
    def test_no_user_recommended_group_page_render(self, mocked):
        self.helper_create_user_node(test_user)
        with self.app as client:
            with client.session_transaction() as session:
                session['uid'] = ""
            res = client.get('/social/groups/recommended')
            print(res.data)
            self.assertTrue(mocked.called, "Recommended Groups Page Render Failed: " + res.data)
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

    @patch('flask.templating._render', return_value='View Group Page Render Works As Expected')
    def test_no_user_view_group_page_render(self, mocked):
        self.helper_create_user_node(test_user)
        self.helper_create_group_node(test_group_node)
        with self.app as client:
            with client.session_transaction() as session:
                session['uid'] = ""
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

    @patch('flask.templating._render', return_value='Route To Manage Group Page Works As Expected')
    def test_no_user_manage_group_page_render(self, mocked):
        self.helper_create_user_node(test_user)
        self.helper_create_group_node(test_group_node)
        self.helper_make_admin_for_group(test_user['google_id'], test_group_node['group_uid'])
        with self.app as client:
            with client.session_transaction() as session:
                session['uid'] = ""
            res = client.get('/social/manage/groups/' + str(test_group_node['group_uid']))
            self.assertFalse(mocked.called, "Route To Manage Group Page Failed: " + res.data)
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

    @patch('flask.templating._render',
           return_value='Delete Group Admin & Removing Admin Privilieges For Group Admin Works As Expected')
    def test_delete_group_admin_or_make_member(self, mocked):
        self.helper_create_user_node(test_user)
        self.helper_create_user_node(test_user_group)
        self.helper_create_group_node(test_group_node)
        self.helper_make_admin_for_group(test_user['google_id'], test_group_node['group_uid'])
        self.helper_make_admin_for_group(test_user_group['google_id'], test_group_node['group_uid'])
        with self.app as client:
            with client.session_transaction() as session:
                session['uid'] = test_user['sql_id']

            res = client.post('/social/manage/groups/delete_group_admin_or_make_member',
                              data=dict(group_uid=test_group_node['group_uid'],
                                        google_id=test_user_group['google_id'], submit="DeleteAdmin"))
            self.assertFalse(mocked.called, "Delete Admin Of A Group Failed: " + res.data)

            self.helper_make_admin_for_group(test_user_group['google_id'], test_group_node['group_uid'])
            res = client.post('/social/manage/groups/delete_group_admin_or_make_member',
                              data=dict(group_uid=test_group_node['group_uid'],
                                        google_id=test_user_group['google_id'], submit="MakeMember"))
            self.assertFalse(mocked.called, "Removing Admin Privilieges For Group Admin Group Failed: " + res.data)

        self.helper_leave_group(test_user_group['google_id'], test_group_node['group_uid'])
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

    @patch('flask.templating._render', return_value='Get Users JSON To Invite For Group Works As Expected')
    def test_get_users_to_invite_groups(self, mocked):
        self.helper_create_user_node(test_user)
        self.helper_create_group_node(test_group_node)
        with self.app as client:
            with client.session_transaction() as session:
                session['uid'] = test_user['sql_id']
            res = client.get('/social/groups/get_users_to_invite_groups/' + str(test_group_node['group_uid']))
            self.assertFalse(mocked.called, "Get Users JSON To Invite For Group Failed: " + res.data)
        self.helper_delete_group_node(test_group_node)
        self.helper_delete_user_node(test_user)

    @patch('flask.templating._render', return_value='Get Users JSON To Invite For Group Works As Expected')
    def test_no_user_get_users_to_invite_groups(self, mocked):
        self.helper_create_user_node(test_user)
        self.helper_create_group_node(test_group_node)
        with self.app as client:
            with client.session_transaction() as session:
                session['uid'] = ""
            res = client.get('/social/groups/get_users_to_invite_groups/' + str(test_group_node['group_uid']))
            self.assertFalse(mocked.called, "Get Users JSON To Invite For Group Failed: " + res.data)
        self.helper_delete_group_node(test_group_node)
        self.helper_delete_user_node(test_user)

    @patch('flask.templating._render', return_value='Get Groups JSON Works As Expected')
    def test_get_groups_json(self, mocked):
        with self.app as client:
            res = client.get('/social/get_groups')
            self.assertFalse(mocked.called, "Get Groups JSON Failed: " + res.data)

    @patch('flask.templating._render', return_value='Invite Group Member Works As Expected')
    def test_invite_group_member(self, mocked):
        self.helper_create_user_node(test_user)
        self.helper_create_user_node(test_user_group)
        self.helper_create_group_node(test_group_node)
        self.helper_make_admin_for_group(test_user['google_id'], test_group_node['group_uid'])
        with self.app as client:
            with client.session_transaction() as session:
                session['uid'] = test_user['sql_id']
            res = client.post('/social/manage/groups/invite_group_member',
                              data=dict(google_id=test_user_group['google_id'],
                                        group_uid=test_group_node['group_uid']))
            self.assertFalse(mocked.called, "Invite Group Member Failed: " + res.data)
        self.helper_leave_group(test_user_group['google_id'], test_group_node['group_uid'])
        self.helper_leave_group(test_user['google_id'], test_group_node['group_uid'])
        self.helper_delete_group_node(test_group_node)
        self.helper_delete_user_node(test_user_group)
        self.helper_delete_user_node(test_user)

    @patch('flask.templating._render', return_value='Join / Leave Group Works As Expected')
    def test_join_leave_group(self, mocked):
        self.helper_create_user_node(test_user)
        self.helper_create_group_node(test_group_node)
        with self.app as client:
            with client.session_transaction() as session:
                session['uid'] = test_user['sql_id']

            res = client.post(
                "/social/manage/groups/join_leave?next=/social/groups/" + str(test_group_node['group_uid']),
                data=dict(google_id=test_user['google_id'],
                          group_uid=test_group_node['group_uid'],
                          is_private_group=test_group_node['is_private_group'],
                          submit="Join"))
            self.assertFalse(mocked.called, "Join Group Member Failed: " + res.data)

            self.helper_leave_group(test_user['google_id'], test_group_node['group_uid'])
            self.helper_make_admin_for_group(test_user['google_id'], test_group_node['group_uid'])
            res = client.post(
                "/social/manage/groups/join_leave?next=/social/groups/" + str(test_group_node['group_uid']),
                data=dict(google_id=test_user['google_id'],
                          group_uid=test_group_node['group_uid'],
                          is_private_group=test_group_node['is_private_group'],
                          submit="Leave"))
            self.assertFalse(mocked.called, "Leave Group Member Failed: " + res.data)

        self.helper_delete_group_node(test_group_node)
        self.helper_delete_user_node(test_user)

    # --------------------------------------------------------------------------------------
    # System Page Tests
    # --------------------------------------------------------------------------------------

    @patch('flask.templating._render', return_value='Add system post Works As Expected')
    def test_add_system_post(self, mocked):
        self.helper_create_user_node(test_user)
        self.helper_create_system_node(test_system_node)
        with self.app as client:
            with client.session_transaction() as session:
                session['uid'] = test_user['sql_id']
            res = client.post('/social/systems/add_system_post',
                              data=dict(system_uid=system_uid, privacy="public", text="This is a test system post",
                                        link="None", link_title="None", link_img="None", link_description="None"))
            self.assertFalse(mocked.called, "Add system post Failed: " + res.data)
        self.helper_delete_system_node(test_system_node)
        self.helper_delete_user_node(test_user)
        self.helper_delete_system_posts()

    @patch('flask.templating._render', return_value='Delete system post Works As Expected')
    def test_delete_system_post(self, mocked):
        self.helper_create_user_node(test_user)
        self.helper_create_system_node(test_system_node)
        self.helper_create_system_post_node(test_system_post_node)
        with self.app as client:
            with client.session_transaction() as session:
                session['uid'] = test_user['sql_id']
            res = client.post('/social/delete_system_post',
                              data=dict(system_uid=system_uid, postid=post_system_id))
            # print(res.data)
            self.assertFalse(mocked.called, "Delete system post Failed: " + res.data)
        self.helper_delete_system_node(test_system_node)
        self.helper_delete_user_node(test_user)

    @patch('flask.templating._render', return_value='Edit system post Works As Expected')
    def test_edit_system_post(self, mocked):
        self.helper_create_user_node(test_user)
        self.helper_create_system_node(test_system_node)
        self.helper_create_system_post_node(test_system_post_node)
        with self.app as client:
            with client.session_transaction() as session:
                session['uid'] = test_user['sql_id']
            res = client.post('/social/edit_system_post',
                              data=dict(system_uid=system_uid, postid=post_system_id,
                                        editedpost="This is an edited post"))
            self.assertFalse(mocked.called, "Edit system post Failed: " + res.data)
        self.helper_delete_system_post_node(post_system_id)
        self.helper_delete_system_node(test_system_node)
        self.helper_delete_user_node(test_user)

    @patch('flask.templating._render', return_value='Add system comment Works As Expected')
    def test_add_system_comment(self, mocked):
        self.helper_create_user_node(test_user)
        self.helper_create_system_node(test_system_node)
        self.helper_create_system_post_node(test_system_post_node)
        with self.app as client:
            with client.session_transaction() as session:
                session['uid'] = test_user['sql_id']
            res = client.post('/social/add_system_comment',
                              data=dict(system_uid=system_uid, postid=int(test_system_post_node['id']),
                                        newcomment="This is a new system comment"))
            # print(res.data)
            self.assertFalse(mocked.called, "Add system comment Failed: " + res.data)
        self.helper_delete_system_post_node(test_system_post_node['id'])
        self.helper_delete_system_node(test_system_node)
        self.helper_delete_user_node(test_user)
        self.helper_delete_system_comment()

    @patch('flask.templating._render', return_value='Like system post Works As Expected')
    def test_like_system_post(self, mocked):
        self.helper_create_user_node(test_user)
        self.helper_create_system_node(test_system_node)
        self.helper_create_system_post_node(test_system_post_node)
        with self.app as client:
            with client.session_transaction() as session:
                session['uid'] = test_user['sql_id']
            res = client.post('/social/like_or_unlike_system_post',
                              data=dict(system_uid=system_uid, postid=int(test_system_post_node['id']),
                                        submit="likePost"))
            # print(res.data)
            self.assertFalse(mocked.called, "Like system post Failed: " + res.data)
        self.helper_delete_system_post_node(test_system_post_node['id'])
        self.helper_delete_system_node(test_system_node)
        self.helper_delete_user_node(test_user)

    @patch('flask.templating._render', return_value='UnLike system post Works As Expected')
    def test_unlike_system_post(self, mocked):
        self.helper_create_user_node(test_user)
        self.helper_create_system_node(test_system_node)
        self.helper_create_system_post_node(test_system_post_node)
        with self.app as client:
            with client.session_transaction() as session:
                session['uid'] = test_user['sql_id']
            res = client.post('/social/like_or_unlike_system_post',
                              data=dict(system_uid=system_uid, postid=int(test_system_post_node['id']),
                                        submit="unlikePost"))
            # print(res.data)
            self.assertFalse(mocked.called, "UnLike system post Failed: " + res.data)
        self.helper_delete_system_post_node(test_system_post_node['id'])
        self.helper_delete_system_node(test_system_node)
        self.helper_delete_user_node(test_user)

    @patch('flask.templating._render', return_value='Edit system comment Works As Expected')
    def test_edit_system_comment(self, mocked):
        self.helper_create_user_node(test_user)
        self.helper_create_system_node(test_system_node)
        self.helper_create_system_post_node(test_system_post_node)
        self.helper_create_system_comment_node(test_system_comment)
        with self.app as client:
            with client.session_transaction() as session:
                session['uid'] = test_user['sql_id']
            res = client.post('/social/edit_or_delete_system_comment',
                              data=dict(system_uid=system_uid, commentid=test_system_comment_id,
                                        editedcomment="This is test edited comment",
                                        submit="editComment"))
            # print(res.data)
            self.assertFalse(mocked.called, "Edit system comment Failed: " + res.data)
        self.helper_delete_system_post_node(test_system_post_node['id'])
        self.helper_delete_system_comment_node(test_system_comment['id'])
        self.helper_delete_system_node(test_system_node)
        self.helper_delete_user_node(test_user)

    @patch('flask.templating._render', return_value='Delete system comment Works As Expected')
    def test_delete_system_comment(self, mocked):
        self.helper_create_user_node(test_user)
        self.helper_create_system_node(test_system_node)
        self.helper_create_system_post_node(test_system_post_node)
        self.helper_create_system_comment_node(test_system_comment)
        with self.app as client:
            with client.session_transaction() as session:
                session['uid'] = test_user['sql_id']
            res = client.post('/social/edit_or_delete_system_comment',
                              data=dict(system_uid=system_uid, commentid=test_system_comment_id,
                                        submit="deleteComment"))
            # print(res.data)
            self.assertFalse(mocked.called, "Delete system comment Failed: " + res.data)
        self.helper_delete_system_post_node(post_system_id)
        self.helper_delete_system_node(test_system_node)
        self.helper_delete_user_node(test_user)

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

    @patch('flask.templating._render', return_value='Route To Search Systems Page Works As Expected')
    def test_search_systems_no_user_page_render(self, mocked):
        self.helper_create_user_node(test_user)
        with self.app as client:
            with client.session_transaction() as session:
                session['uid'] = ""
            res = client.get('/social/systems/')
            print(res.data)
            self.assertTrue(mocked.called, "Route To Search Systems Page Failed: " + res.data)
        self.helper_delete_user_node(test_user)

    @patch('flask.templating._render', return_value='Route To My Systems Page Works As Expected')
    def test_my_systems_page_render(self, mocked):
        self.helper_create_user_node(test_user)
        with self.app as client:
            with client.session_transaction() as session:
                session['uid'] = test_user['sql_id']
            res = client.get('/social/systems/self')
            print(res.data)
            self.assertTrue(mocked.called, "Route To My Systems Page Failed: " + res.data)
        self.helper_delete_user_node(test_user)

    @patch('flask.templating._render', return_value='Route To My Systems Page Works As Expected')
    def test_my_systems_no_user_page_render(self, mocked):
        self.helper_create_user_node(test_user)
        with self.app as client:
            with client.session_transaction() as session:
                session['uid'] = ""
            res = client.get('/social/systems/self')
            print(res.data)
            self.assertTrue(mocked.called, "Route To My Systems Page Failed: " + res.data)
        self.helper_delete_user_node(test_user)

    @patch('flask.templating._render', return_value='Route To All Systems Page Works As Expected')
    def test_all_systems_page_render(self, mocked):
        self.helper_create_user_node(test_user)
        with self.app as client:
            with client.session_transaction() as session:
                session['uid'] = test_user['sql_id']
            res = client.get('/social/systems/all')
            print(res.data)
            self.assertTrue(mocked.called, "Route To All Systems Page Failed: " + res.data)
        self.helper_delete_user_node(test_user)

    @patch('flask.templating._render', return_value='Route To All Systems Page Works As Expected')
    def test_all_systems_no_user_page_render(self, mocked):
        self.helper_create_user_node(test_user)
        with self.app as client:
            with client.session_transaction() as session:
                session['uid'] = ""
            res = client.get('/social/systems/all')
            print(res.data)
            self.assertTrue(mocked.called, "Route To All Systems Page Failed: " + res.data)
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

    @patch('flask.templating._render', return_value='Search Systems Post Method Works As Expected')
    def test_search_systems(self, mocked):
        self.helper_create_user_node(test_user)
        self.helper_create_system_node(test_system_node)
        with self.app as client:
            with client.session_transaction() as session:
                session['uid'] = ""
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

    @patch('flask.templating._render', return_value='Route To System Page Works As Expected')
    def test_view_no_user_system_page_render(self, mocked):
        self.helper_create_user_node(test_user)
        self.helper_create_system_node(test_system_node)
        with self.app as client:
            with client.session_transaction() as session:
                session['uid'] = ""
            res = client.get('/social/systems/' + str(system_uid))
            print(res.data)
            self.assertTrue(mocked.called, "Route To System Page Failed: " + res.data)
        self.helper_delete_system_node(test_system_node)
        self.helper_delete_user_node(test_user)

    @patch('flask.templating._render', return_value='Route To System Page Works As Expected')
    def test_view_wrong_user_system_page_render(self, mocked):
        self.helper_create_user_node(test_user)
        self.helper_create_system_node(test_system_node)
        with self.app as client:
            with client.session_transaction() as session:
                session['uid'] = "989898898989"
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

    @patch('flask.templating._render', return_value='Route To Manage System Page Works As Expected')
    def test_no_user_manage_systems_page_render(self, mocked):
        self.helper_create_user_node(test_user)
        self.helper_create_system_node(test_system_node)
        self.helper_make_admin_for_system(test_user['google_id'], test_system_node['system_uid'])
        with self.app as client:
            with client.session_transaction() as session:
                session['uid'] = ""
            res = client.get('/social/manage/systems/' + str(system_uid))
            self.assertFalse(mocked.called, "Route To Manage System Page Failed: " + res.data)
        self.helper_leave_system(test_user['google_id'], test_system_node['system_uid'])
        self.helper_delete_system_node(test_system_node)
        self.helper_delete_user_node(test_user)

    @patch('flask.templating._render', return_value='Route To Manage System Page Works As Expected')
    def test_wrong_user_manage_systems_page_render(self, mocked):
        self.helper_create_user_node(test_user)
        self.helper_create_system_node(test_system_node)
        self.helper_make_admin_for_system(test_user['google_id'], test_system_node['system_uid'])
        with self.app as client:
            with client.session_transaction() as session:
                session['uid'] = "121212"
            res = client.get('/social/manage/systems/' + str(system_uid))
            self.assertFalse(mocked.called, "Route To Manage System Page Failed: " + res.data)
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

    # Helper Function To Delete System Comment In Neo4J Database
    def helper_delete_system_comment(self):
        try:
            delete_system_comment_query = """
                MATCH (u:SystemComment)
                WHERE u.content = {content}
                DETACH DELETE u
            """
            delete_user_status = graph.cypher.execute(delete_system_comment_query,
                                                      content="This is a new system comment")
        except Exception as ex:
            print "Exception At helper_delete_system_comment: " + str(ex.message)

    # Helper Function To Delete User Post In Neo4J Database
    def helper_delete_user_posts(self):
        try:
            delete_user_post_query = """
                MATCH (u:Post)
                WHERE u.text = {text}
                DETACH DELETE u
            """
            delete_user_status = graph.cypher.execute(delete_user_post_query, text="This is a test post")
        except Exception as ex:
            print "Exception At helper_delete_user_posts: " + str(ex.message)

    # Helper Function To Delete User Group Node In Neo4J Database
    def helper_delete_group_posts(self):
        try:
            delete_group_posts_query = """
                MATCH (u:GroupPost)
                WHERE u.text = {text}
                DETACH DELETE u
            """
            delete_user_status = graph.cypher.execute(delete_group_posts_query, text="This is a test group post")
        except Exception as ex:
            print "Exception At helper_delete_group_posts: " + str(ex.message)

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

    # Helper function for send friend request
    def helper_send_friend_request(self, sql_id):
        try:
            User(test_user['sql_id']).send_friend_request(sql_id)
        except Exception as ex:
            print "Exception At helper_send_friend_request: " + str(ex.message)

    # Helper function for creating friend relation
    def helper_make_friend(self, google_id):
        try:
            User(test_user['sql_id']).accept_friend_request(google_id)
        except Exception as ex:
            print "Exception At helper_make_friends: " + str(ex.message)

    # Helper function for delete friend relation
    def helper_delete_friend(self, google_id):
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

    # Helper Function To Create Group Post Node In Neo4J Database
    def helper_create_group_post_node(self, group_post_node_to_create):
        try:
            # Same Group Post Node If Exists Is Removed
            self.helper_delete_group_post_node(group_post_node_to_create['id'])
            graph.create(group_post_node_to_create)
        except Exception as ex:
            print "Exception At helper_create_group_post_node: " + str(ex.message)

            # Helper Function To Delete User Post Node In Neo4J Database

    def helper_delete_group_post_node(self, group_post_to_delete):
        try:
            delete_group_post_query = """
                MATCH (g:GroupPost)
                WHERE g.id = {postid}
                DETACH DELETE g
            """
            delete_group_status = graph.cypher.execute(delete_group_post_query, postid=group_post_to_delete)
        except Exception as ex:
            print "Exception At helper_delete_group_post_node: " + str(ex.message)

    # Helper Function To Create System Post Node In Neo4J Database
    def helper_create_system_post_node(self, system_post_node_to_create):
        try:
            # Same System Post Node If Exists Is Removed
            self.helper_delete_system_post_node(post_system_id)
            graph.create(system_post_node_to_create)
        except Exception as ex:
            print "Exception At helper_create_system_post_node: " + str(ex.message)

            # Helper Function To Delete System Post Node In Neo4J Database

    def helper_delete_system_post_node(self, system_post_to_delete):
        try:
            delete_system_post_query = """
                MATCH (s:SystemPost)
                WHERE s.id = {postid}
                DETACH DELETE s
            """
            delete_system_status = graph.cypher.execute(delete_system_post_query, postid=system_post_to_delete)
        except Exception as ex:
            print "Exception At helper_delete_system_post_node: " + str(ex.message)

    # Helper Function To Create  Post Node In Neo4J Database
    def helper_create_post_node(self, post_node_to_create):
        try:
            # Same  Post Node If Exists Is Removed
            self.helper_delete_post_node(post_node_to_create['id'])
            graph.create(post_node_to_create)
        except Exception as ex:
            print "Exception At helper_create_post_node: " + str(ex.message)

            # Helper Function To Delete  Post Node In Neo4J Database

    def helper_delete_post_node(self, post_to_delete):
        try:
            delete_post_query = """
                MATCH (s:Post)
                WHERE s.id = {postid}
                DETACH DELETE s
            """
            delete_status = graph.cypher.execute(delete_post_query, postid=post_to_delete)
        except Exception as ex:
            print "Exception At helper_delete_post_node: " + str(ex.message)

    # Helper Function To Create System comment Node In Neo4J Database
    def helper_create_system_comment_node(self, system_comment_node_to_create):
        try:
            # Same System comment Node If Exists Is Removed
            self.helper_delete_system_comment_node(system_comment_node_to_create['id'])
            graph.create(system_comment_node_to_create)
        except Exception as ex:
            print "Exception At helper_create_system_comment_node: " + str(ex.message)

            # Helper Function To Delete System comment Node In Neo4J Database

    def helper_delete_system_comment_node(self, system_comment_to_delete):
        try:
            delete_system_comment_query = """
                MATCH (s:SystemComment)
                WHERE s.id = {commentid}
                DETACH DELETE s
            """
            delete_system_status = graph.cypher.execute(delete_system_comment_query, commentid=system_comment_to_delete)
        except Exception as ex:
            print "Exception At helper_delete_system_comment_node: " + str(ex.message)

    # Helper Function To Create group comment Node In Neo4J Database
    def helper_create_group_comment_node(self, group_comment_node_to_create):
        try:
            # Same group comment Node If Exists Is Removed
            self.helper_delete_group_comment_node(test_group_comment['id'])
            graph.create(group_comment_node_to_create)
        except Exception as ex:
            print "Exception At helper_create_group_comment_node: " + str(ex.message)

            # Helper Function To Delete group comment Node In Neo4J Database

    def helper_delete_group_comment_node(self, group_comment_to_delete):
        try:
            delete_group_comment_query = """
                MATCH (g:GroupComment)
                WHERE g.id = {commentid}
                DETACH DELETE g
            """
            delete_group_status = graph.cypher.execute(delete_group_comment_query, commentid=group_comment_to_delete)
        except Exception as ex:
            print "Exception At helper_delete_group_comment_node: " + str(ex.message)

    # Helper Function To Create comment Node In Neo4J Database
    def helper_create_comment_node(self, comment_node_to_create):
        try:
            # Same  comment Node If Exists Is Removed
            self.helper_delete_comment_node(comment_node_to_create['id'])
            graph.create(comment_node_to_create)
        except Exception as ex:
            print "Exception At helper_create_comment_node: " + str(ex.message)

            # Helper Function To Delete comment Node In Neo4J Database

    def helper_delete_comment_node(self, comment_to_delete):
        try:
            delete_comment_query = """
                MATCH (c:Comment)
                WHERE c.id = {commentid}
                DETACH DELETE c
            """
            delete_status = graph.cypher.execute(delete_comment_query, commentid=comment_to_delete)
        except Exception as ex:
            print "Exception At helper_delete_comment_node: " + str(ex.message)

    # Helper Function To Delete User System Node In Neo4J Database
    def helper_delete_system_posts(self):
        try:
            delete_system_posts_query = """
                MATCH (u:SystemPost)
                WHERE u.text = {text}
                DETACH DELETE u
            """
            delete_user_status = graph.cypher.execute(delete_system_posts_query, text="This is a test system post")
        except Exception as ex:
            print "Exception At helper_delete_system_posts: " + str(ex.message)

    # Helper Function To Delete User Comment In Neo4J Database
    def helper_delete_comment(self):
        try:
            delete_comment_query = """
                MATCH (u:Comment)
                WHERE u.content = {content}
                DETACH DELETE u
            """
            delete_user_status = graph.cypher.execute(delete_comment_query, content="This is a test comment")
        except Exception as ex:
            print "Exception At helper_delete_comment: " + str(ex.message)

    # Helper Function To Delete group Comment In Neo4J Database
    def helper_delete_group_comment(self):
        try:
            delete_group_comment_query = """
                MATCH (u:GroupComment)
                WHERE u.content = {content}
                DETACH DELETE u
            """
            delete_user_status = graph.cypher.execute(delete_group_comment_query, content="This is a new group comment")
        except Exception as ex:
            print "Exception At helper_delete_group_comment: " + str(ex.message)

    # --------------------------------------------------------------------------------------

    if __name__ == '__main__':
        unittest.main()
