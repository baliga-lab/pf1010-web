from py2neo import Graph, Node, Relationship, cypher
import time
import datetime
import uuid
import requests
import json

############################################################################
# function : init_sc_app
# purpose : Initialize the app_instance and graph_instance
# params :
#        app - instance of social app
# returns : None
# Exceptions : None
############################################################################
def init_sc_app(app):
    global app_instance
    global graph_instance
    app_instance = app
    graph_instance = Graph(get_app_instance().config['CONNECTIONSETTING'])

############################################################################
# function : get_app_instance
# purpose : Return the app_instance
# params : None
# returns : app_instance social app instance
# Exceptions : None
############################################################################
def get_app_instance():
    return app_instance

############################################################################
# function : getGraphConnectionURI
# purpose : Create / Load graph with the connection settings
# params : None
# returns : graph_instance social app graph instance
# Exceptions : None
############################################################################
def getGraphConnectionURI():
    return graph_instance

################################################################################
# Class : User
# Contains information related to the user who is logged in
################################################################################
class User:
    ############################################################################
    # function : __init__
    # purpose : main function sets sql_id
    # params :
    #       sql_id : sql_id for user
    # returns : None
    # Exceptions : None
    ############################################################################

    def __init__(self, sql_id):
        self.sql_id = sql_id

    ############################################################################
    # function : find
    # purpose : function used to find user name based on sql_id
    # params : self (User)
    # returns : User node
    # Exceptions : cypher.CypherError, cypher.CypherTransactionError
    ############################################################################

    def find(self):
        try:
            user = getGraphConnectionURI().find_one("User", "sql_id", self.sql_id)
            return user
        except cypher.CypherError, cypher.CypherTransactionError:
            raise "Exception occured in function User.find()"

    ############################################################################
    # function : updateprofile
    # purpose : function used to update the user profile
    # params :
    #        displayname : display name which need to changed
    #        dob : date of birth for the user
    # returns : Boolean
    # Exceptions : General Exception
    ############################################################################

    def updateprofile(self, givenName, familyName, displayname, gender, organization, user_type, dateofbirth):
        query = """
        MATCH(x:User)
        WHERE x.sql_id = {sql_id}
        SET x.givenName = {newGivenName}, x.familyName = {newFamilyName},
         x.displayName = {newdisplayname}, x.gender = {newGender}, x.organization = {newOrganization}, x.user_type={newUserType}, x.dob = {newDOB}
        """
        try:
            return getGraphConnectionURI().cypher.execute(query, sql_id=self.sql_id, newGivenName=givenName,
                                                          newFamilyName=familyName,
                                                          newdisplayname=displayname,
                                                          newGender=gender, newOrganization=organization,
                                                          newUserType=user_type, newDOB=dateofbirth)
        except Exception as e:
            print str(e)
            raise "Exception occured in function updateprofile()"

    ############################################################################
    # function : verify_password
    # purpose : function which checks if the possword is correct
    # params :
    #        password : password which needs to be verified
    # returns : Boolean
    # Exceptions : None
    ############################################################################

    def verify_password(self, password):
        user = self.find()
        if user:
            return True
        else:
            return False

    ############################################################################
    # function : add_post
    # purpose : Adds new post node in neo4j with the given information and creates
    #            POSTED relationship between Post and User node
    # params :
    #        text : contains the data shared in post
    #        privacy : privacy level of the post
    #        link : contains the link information
    # returns : None
    # Exceptions : cypher.CypherError, cypher.CypherTransactionError
    ############################################################################

    def add_post(self, text, privacy, link, profile=None):
        user = self.find()
        post = Node(
            "Post",
            id=str(uuid.uuid4()),
            text=text,
            link=link,
            privacy=privacy,
            creation_time=timestamp(),
            modified_time=timestamp(),
            date=date()
        )

        rel_post = Relationship(user, "POSTED", post)
        # if it is published in someone else's profile page
        if profile:
            rel_posted_to = Relationship(post, "POSTED_TO", profile)
        try:
            getGraphConnectionURI().create(rel_post)
            # if it is published in someone else's profile page
            if profile:
                getGraphConnectionURI().create(rel_posted_to)
        except cypher.CypherError, cypher.CypherTransactionError:
            raise "Exception occured in function add_post "

    ############################################################################
    # function : add_post_to
    # purpose : Adds new post node in neo4j with the given information and creates
    #            POSTED relationship between Post and User node
    # params :
    #        text : contains the data shared in post
    #        privacy : privacy level of the post
    #        link : contains the link information
    #        page_type: type of page where it was posted to
    #        page_id: id of user whose timeline this was posted to
    # returns : None
    # Exceptions : cypher.CypherError, cypher.CypherTransactionError
    ############################################################################

    def add_post_to(self, user_id, posted_to_id):
        query = """
        MATCH (u:User {sql_id: {sql_id}})-[:POSTED]->(post:Post)
        RETURN ID(post) as post_id
        ORDER BY post.creation_time DESC limit 1
        """
        command = """
        MATCH (u:User {sql_id: {sql_id}}), (post:Post)
        WHERE ID(post) = {post_id}
        CREATE (p)-[:POSTED_TO]->(u)"
        """
        try:
            post_node = getGraphConnectionURI().cypher.execute(query, {'sql_id': user_id})
            getGraphConnectionURI().cypher.execute(command,
                                                   {'sql_id': posted_to_id, 'post_id': post_node[0]['post_id']})
        except cypher.CypherError, cypher.CypherTransactionError:
            raise "Exception occured in function add_post_to "

    ############################################################################
    # function : test_add_post
    # purpose : Adds new post node in neo4j with the given information and id 1
    #           and creates POSTED relationship between Post and User node
    # params :
    #        text : contains the data shared in post
    #        privacy : privacy level of the post
    #        link : contains the link information
    # returns : None
    # Exceptions : cypher.CypherError, cypher.CypherTransactionError
    ############################################################################

    def test_add_post(self, text, privacy, link):
        user = self.find()
        post = Node(
            "Post",
            id=str(1),
            text=text,
            link=link,
            privacy=privacy,
            creation_time=timestamp(),
            modified_time=timestamp(),
            date=date()
        )
        rel = Relationship(user, "POSTED", post)
        try:
            getGraphConnectionURI().create(rel)
        except cypher.CypherError, cypher.CypherTransactionError:
            raise "Exception occured in function test_add_post "

    ############################################################################
    # function : edit_post
    # purpose : Edits post node in neo4j with the given id
    # params :
    #        newcontent : contains the data shared in comment
    #        postid : comment id which is being added
    # Exceptions : cypher.CypherError, cypher.CypherTransactionError
    # returns : None
    ############################################################################

    def edit_post(self, newcontent, postid):
        query = """
        MATCH (post:Post)
        WHERE post.id = {postid}
        SET post.text = {newcontent}
        RETURN post
        """
        try:
            getGraphConnectionURI().cypher.execute(query, postid=postid, newcontent=newcontent);
        except cypher.CypherError, cypher.CypherTransactionError:
            raise "Exception occured in function edit_post"

    ############################################################################
    # function : get_user_sql_id
    # purpose : get users sql id
    # params :
    #
    # Exceptions : cypher.CypherError, cypher.CypherTransactionError
    # returns : user_sql_id
    ############################################################################

    def get_user_sql_id(self):
        user = self.find()
        return self.sql_id

    ############################################################################
    # function : delete_post
    # purpose : deletes comments and all related relationships first
    #           and then deletes post and all relationships
    # params :
    #        postid : post id for which user liked
    # returns : None
    # Exceptions : cypher.CypherError, cypher.CypherTransactionError
    ############################################################################

    def delete_post(self, postid):
        user = self.find()
        post = getGraphConnectionURI().find_one("Post", "id", postid)

        # Deletes comments and all related relationships

        deleteCommentsQuery = """
            MATCH (post:Post)-[r:HAS]->(comment:Comment)
            WHERE post.id= {postid}
            DETACH DELETE comment
            """
        try:
            getGraphConnectionURI().cypher.execute(deleteCommentsQuery, postid=postid)
        except cypher.CypherError, cypher.CypherTransactionError:
            raise "Exception occured in function delete_post : deleteCommentsQuery "

        # Deletes posts and all related relationships

        deletePostQuery = """
            MATCH (post:Post)
            WHERE post.id= {postid}
            DETACH DELETE post
            """
        try:
            getGraphConnectionURI().cypher.execute(deletePostQuery, postid=postid)
        except cypher.CypherError, cypher.CypherTransactionError:
            raise "Exception occured in function delete_post : deletePostQuery "

    ############################################################################
    # function : add_comment
    # purpose : Adds new comment node in neo4j with the given information and creates
    #            POSTED relationship between Post and User node
    # params :
    #        newcomment : contains the data shared in comment
    #        postid : post id for which the comment has been added
    # Exceptions : cypher.CypherError, cypher.CypherTransactionError
    # returns : None
    ############################################################################

    def add_comment(self, newcomment, postid):
        user = self.find()
        # print(user)
        comment = Node(
            "Comment",
            id=str(uuid.uuid4()),
            content=newcomment,
            user_sql_id=self.sql_id,
            user_display_name=user['displayName'],
            creation_time=timestamp(),
            modified_time=timestamp())

        try:
            post = getGraphConnectionURI().find_one("Post", "id", postid)
            rel = Relationship(post, 'HAS', comment)
            getGraphConnectionURI().create(rel)
        except cypher.CypherError, cypher.CypherTransactionError:
            raise "Exception occured in function add_comment "

    ############################################################################
    # function : test_add_comment
    # purpose : Adds new comment node in neo4j with the given information and creates
    #            POSTED relationship between Post and User node with id 1
    # params :
    #        newcomment : contains the data shared in comment
    #        postid : post id for which the comment has been added
    # Exceptions : cypher.CypherError, cypher.CypherTransactionError
    # returns : None
    ############################################################################

    def test_add_comment(self, newcomment, postid):
        user = self.find()
        # print(user)
        comment = Node(
            "Comment",
            id=str(1),
            content=newcomment,
            user_sql_id=self.sql_id,
            user_display_name=user['displayName'],
            creation_time=timestamp(),
            modified_time=timestamp())
        post = getGraphConnectionURI().find_one("Post", "id", postid)
        rel = Relationship(post, 'HAS', comment)
        try:
            getGraphConnectionURI().create(rel)
        except cypher.CypherError, cypher.CypherTransactionError:
            raise "Exception occured in function test_add_comment "

    ############################################################################
    # function : edit_comment
    # purpose : Edits comment node in neo4j with the given id
    # params :
    #        newcomment : contains the data shared in comment
    #        commentid : comment id which is being added
    # Exceptions : cypher.CypherError, cypher.CypherTransactionError
    # returns : None
    ############################################################################

    def edit_comment(self, newcomment, commentid):
        user = self.find()
        print(commentid)
        query = """
        MATCH (comment:Comment)
        WHERE comment.id = {commentid}
        SET comment.content = {newcomment}
        RETURN comment
        """
        try:
            getGraphConnectionURI().cypher.execute(query, commentid=commentid, newcomment=newcomment);
        except cypher.CypherError, cypher.CypherTransactionError:
            raise "Exception occured in function edit_comment"

    ############################################################################
    # function : delete_comment
    # purpose : deletes comment node in neo4j with the given id
    # params :
    #        commentid : comment id which is being added
    # Exceptions : cypher.CypherError, cypher.CypherTransactionError
    # returns : None
    ############################################################################

    def delete_comment(self, commentid):
        user = self.find()
        print("Comment id" + str(commentid))
        query = """
        MATCH (comment:Comment)
        WHERE comment.id = {commentid}
        DETACH DELETE comment
        """
        try:
            getGraphConnectionURI().cypher.execute(query, commentid=commentid);
        except cypher.CypherError, cypher.CypherTransactionError:
            raise "Exception occured in function delete_comment "

    ############################################################################
    # function : like_post
    # purpose : creates a unique LIKED relationship between User and Post
    # params :
    #        postid : post id for which user liked
    # returns : None
    # Exceptions : cypher.CypherError, cypher.CypherTransactionError
    ############################################################################

    def like_post(self, postid):
        user = self.find()
        post = getGraphConnectionURI().find_one("Post", "id", postid)
        rel = Relationship(user, 'LIKED', post)
        try:
            getGraphConnectionURI().create_unique(rel)
        except cypher.CypherError, cypher.CypherTransactionError:
            raise "Exception occured in function like_post "

    ############################################################################
    # function : unlike_post
    # purpose : removes LIKED relationship between User and Post
    # params :
    #        postid : post id for which user liked
    # returns : None
    # Exceptions : cypher.CypherError, cypher.CypherTransactionError
    ############################################################################

    def unlike_post(self, postid):
        userSqlId = self.sql_id
        query = """
            MATCH (u:User)-[r:LIKED]->(p:Post)
            WHERE p.id= {postid} and u.sql_id = {userSqlId}
            DELETE r
        """

        try:
            getGraphConnectionURI().cypher.execute(query, postid=postid, userSqlId=userSqlId);
        except cypher.CypherError, cypher.CypherTransactionError:
            raise "Exception occured in function get_search_friends"

    ############################################################################
    # function : get_search_friends
    # purpose : gets all the friends that is present in the Neo4J database
    # params : None
    # returns : Nodes labeled User
    # Exceptions : cypher.CypherError, cypher.CypherTransactionError
    ############################################################################
    def get_search_friends(self):
        query = """
            MATCH (users:User)
            RETURN users.givenName, users.familyName, users.organization, users.sql_id, users.email, users.google_id
        """

        try:
            results = getGraphConnectionURI().cypher.execute(query);
            return results;
        except cypher.CypherError, cypher.CypherTransactionError:
            raise "Exception occured in function get_search_friends"

    ############################################################################
    # function : get_friends_and_sentreq
    # purpose : used when adding friends to return list of users to be displayed on search screen
    #           of currently logged in user
    # params : None
    # returns : list of friend requests sent by user, friend requests received by user, list of user friends
    # Exceptions : cypher.CypherError, cypher.CypherTransactionError
    ############################################################################
    def get_friends_and_sentreq(self):
        my_sql_id = self.sql_id
        my_sentreq_query = "MATCH (sentrequests { sql_id:{sql_id} })-[:SentRequest]->(res) RETURN res.sql_id"
        my_received_query = "MATCH (receivedrequests { sql_id:{sql_id} })<-[:SentRequest]-(res) RETURN res.sql_id"
        my_friends_query = "MATCH (friends { sql_id:{sql_id} })-[:FRIENDS]-(res) RETURN res.sql_id"

        try:
            sentreq_res = getGraphConnectionURI().cypher.execute(my_sentreq_query, sql_id=my_sql_id);
            receivedreq_res = getGraphConnectionURI().cypher.execute(my_received_query, sql_id=my_sql_id);
            frnds_res = getGraphConnectionURI().cypher.execute(my_friends_query, sql_id=my_sql_id);
            return sentreq_res, receivedreq_res, frnds_res
        except cypher.CypherError, cypher.CypherTransactionError:
            raise "Exception occured in function get_search_friends"

    ############################################################################
    # function : send_friend_request
    # purpose : sends friend request to intended user in the system
    # params : None
    # returns : None
    # Exceptions : cypher.CypherError, cypher.CypherTransactionError
    ############################################################################
    def send_friend_request(self, receiver_sql_id):
        user = self.find()
        user2 = User(int(receiver_sql_id)).find()

        query = """
            MATCH  (n:User),(n1:User)
            Where n.sql_id = {sender_sid} AND n1.sql_id = {receiver_sid}
            CREATE (n)- [r:SentRequest] ->(n1)
            RETURN r
        """
        try:
            results = getGraphConnectionURI().cypher.execute(query, sender_sid=user.properties["sql_id"],
                                                             receiver_sid=user2.properties["sql_id"]);
        except cypher.CypherError, cypher.CypherTransactionError:
            raise "Exception occured in function send_friend_request "

    ############################################################################
    # function : accept_friend_request
    # purpose : accepts friend request from intended user in the system
    # params : None
    # returns : None
    # Exceptions : cypher.CypherError, cypher.CypherTransactionError
    ############################################################################
    def accept_friend_request(self, receiver_sql_id):
        user = self.find()
        user2 = User(int(receiver_sql_id)).find()

        print(date());
        print("In accept_friend_request")
        query = """
            MATCH  (n:User),(n1:User)
            Where n.sql_id = {acceptor_sid} AND n1.sql_id = {accepted_sid}
            CREATE (n)- [r:FRIENDS{date:{today},blocker_id:{blocker_id}}] ->(n1)

        """
        try:
            results = getGraphConnectionURI().cypher.execute(query, acceptor_sid=user.properties["sql_id"],

                                                             accepted_sid=user2.properties["sql_id"], today=date(),
                                                             blocker_id='');

        except cypher.CypherError, cypher.CypherTransactionError:
            raise "Exception occured in function accept_friend_request "

    ############################################################################
    # function : block_a_friend
    # purpose : blocks a friend
    # params : None
    # returns : None
    # Exceptions : cypher.CypherError, cypher.CypherTransactionError
    ############################################################################
    def block_a_friend(self, blocked_sql_id):
        user = self.find()
        user2 = User(int(blocked_sql_id)).find()
        print("In block_a_friend")

        query = """
            match (n1:User)-[r:FRIENDS]-(n2:User)
            where n1.sql_id = {blocker_sid} and n2.sql_id = {blocked_sid}
            set r.blocker_id={blocker_id}
            return r
        """
        try:
            results = getGraphConnectionURI().cypher.execute(query, blocker_sid=user.properties["sql_id"],
                                                             blocked_sid=user2.properties["sql_id"],
                                                             blocker_id=str((user.properties["sql_id"])));
        except cypher.CypherError, cypher.CypherTransactionError:
            raise "Exception occured in function block_a_friend "

    ############################################################################
    # function : unblock_a_friend
    # purpose : unblocks a friend
    # params : None
    # returns : None
    # Exceptions : cypher.CypherError, cypher.CypherTransactionError
    ############################################################################
    def unblock_a_friend(self, blocked_sql_id):
        user = self.find()
        user2 = User(int(blocked_sql_id)).find()
        print("In block_a_friend")
        query = """
            match (n1:User)-[r:FRIENDS]-(n2:User)
            where n1.sql_id = {blocker_sid} and n2.sql_id = {blocked_sid}
            set r.blocker_id={blocker_id};
        """
        try:
            results = getGraphConnectionURI().cypher.execute(query, blocker_sid=user.properties["sql_id"],
                                                             blocked_sid=user2.properties["sql_id"], today=date(),
                                                             blocker_id='');
        except cypher.CypherError, cypher.CypherTransactionError:
            raise "Exception occured in function block_a_friend "

    ############################################################################
    # function : delete_friend_request
    # purpose : delete sent  request on declining or on becoming friends
    # params : None
    # returns : None
    # Exceptions : cypher.CypherError, cypher.CypherTransactionError
    ############################################################################
    def delete_friend_request(self, receiver_sql_id):
        user = self.find()
        user2 = User(int(receiver_sql_id)).find()

        print("In delete_friend_request")
        query = """
            MATCH  (n:User) - [r:SentRequest] - (n1:User)
            Where n.sql_id = {acceptor_sid} AND n1.sql_id = {accepted_sid}
            delete r

        """
        try:
            results = getGraphConnectionURI().cypher.execute(query, acceptor_sid=user.properties["sql_id"],
                                                             accepted_sid=user2.properties["sql_id"]);
        except cypher.CypherError, cypher.CypherTransactionError:
            raise "Exception occured in function delete_friend_request "

    ############################################################################
    # function : delete_friend
    # purpose : delete sent  request on declining or on becoming friends
    # params : None
    # returns : None
    # Exceptions : cypher.CypherError, cypher.CypherTransactionError
    ############################################################################
    def delete_friend(self, receiver_sql_id):
        user = self.find()
        user2 = User(int(receiver_sql_id)).find()

        print("In delete_friend_request")
        query = """
            MATCH  (n:User) - [r:FRIENDS] - (n1:User)
            Where n.sql_id = {acceptor_sid} AND n1.sql_id = {accepted_sid}
            delete r

        """
        try:
            results = getGraphConnectionURI().cypher.execute(query, acceptor_sid=user.properties["sql_id"],
                                                             accepted_sid=user2.properties["sql_id"]);
        except cypher.CypherError, cypher.CypherTransactionError:
            raise "Exception occured in function delete_friend "

    ############################################################################
    # function : get_pending_friend_request
    # purpose : gets the list of friends whose requests are pending
    # params : user_id
    # returns : user node(s)
    # Exceptions : cypher.CypherError, cypher.CypherTransactionError
    ############################################################################
    def get_pending_friend_request(self, u_sql_id):
        query = """
            MATCH (n:User)-[r:SentRequest]->(n1:User)
            WHERE n1.sql_id = {u_sql_id}
            return n
            ORDER BY n.givenName
        """
        try:
            pending_friends_request = getGraphConnectionURI().cypher.execute(query, u_sql_id=u_sql_id)
            return pending_friends_request
        except cypher.CypherError, cypher.CypherTransactionError:
            raise "Exception occured in function get_pending_friend_request"

    ############################################################################
    # function : get_recommended_frnds
    # purpose : get recommended friend list based on mutual friends for the
    #           logged in user if the user is not already friends with those
    #           users and if the user has not already sent that user a friend request
    # params : None
    # returns : name of recommended friends and number of mutual friends
    # Exceptions : cypher.CypherError, cypher.CypherTransactionError
    ############################################################################
    def get_recommended_frnds(self):
        my_sql_id = self.sql_id
        reco_friends_query = """
            MATCH (me { sql_id: {sql_id} })-[:FRIENDS*2..2]-(friend_of_friend)
            WHERE NOT (me)-[:FRIENDS]-(friend_of_friend) AND
            NOT (me)-[:SentRequest]-(friend_of_friend)
            RETURN friend_of_friend.givenName+ " " + friend_of_friend.familyName AS FriendName,
            COUNT(*) AS Num_Mutual_Friends, friend_of_friend.google_id AS gid,
            friend_of_friend.sql_id AS sid,
            friend_of_friend.image_url AS friend_image
            ORDER BY COUNT(*) DESC , FriendName
            """

        try:
            reco_list = getGraphConnectionURI().cypher.execute(reco_friends_query, sql_id=my_sql_id)
            return reco_list
        except cypher.CypherError, cypher.CypherTransactionError:
            raise "Exception occured in function get_recommended_frnds"

    ############################################################################
    # function : get_mutual_friends
    # purpose : get mutual friend information between currently loggedin user and
    #           user who sql_id is passed
    # params : other user sql_id
    # returns : name, sql_id and google_id of recommended friend
    # Exceptions : cypher.CypherError, cypher.CypherTransactionError
    ############################################################################
    def get_mutual_friends(self, other_sid):
        my_sql_id = self.sql_id
        mutual_query = """
        MATCH (me { sql_id: {my_sid} }),(other)
            WHERE other.sql_id = {oth_sid}
            OPTIONAL MATCH pMutualFriends=(me)-[:FRIENDS]-(mf)-[:FRIENDS]-(other)
            RETURN mf.sql_id AS mf_sid, mf.givenName+" "+mf.familyName AS mf_name, mf.google_id AS mf_gid
            """

        try:
            mutual_list = getGraphConnectionURI().cypher.execute(mutual_query, my_sid=my_sql_id, oth_sid=other_sid)
            return mutual_list
        except cypher.CypherError, cypher.CypherTransactionError:
            raise "Exception occured in function get_recommended_frnds"

    ############################################################################
    # function : get_my_friends
    # purpose : to get the logged in user's friend list
    # params : None
    # returns : friend list of the user
    # Exceptions : cypher.CypherError, cypher.CypherTransactionError
    ############################################################################
    def get_my_friends(self, u_sql_id):
        my_sql_id = u_sql_id
        query = """
            MATCH (n:User)-[r:FRIENDS]-(n1:User)
            WHERE n1.sql_id = {sql_id} and r.blocker_id = {blocker_id}
            return n
            ORDER BY n.givenName
        """

        try:
            friendlist = getGraphConnectionURI().cypher.execute(query, sql_id=my_sql_id, blocker_id="");
            return friendlist
        except cypher.CypherError, cypher.CypherTransactionError:
            raise "Exception occured in function get_my_friends"

    ############################################################################
    # function : is_friend
    # purpose : to get whether two users are friends or not
    # params : None
    # returns : boolean, true iff the two users are friends
    # Exceptions : cypher.CypherError, cypher.CypherTransactionError
    ############################################################################
    def is_friend(self, u_sql_id1, u_sql_id2):
        query = """
        MATCH (n:User)-[r:FRIENDS]-(f:User)
        WHERE n.sql_id = {sql_id1} and f.sql_id = {sql_id2} and r.blocker_id = {blocker_id}
        return r
        """
        try:
            friend = getGraphConnectionURI().cypher.execute(query, {'sql_id1': u_sql_id1, 'sql_id2': u_sql_id2,
                                                                    'blocker_id': ""})
            return friend
        except cypher.CypherError, cypher.CypherTransactionError:
            raise "Exception occured in function is_friend"

    ############################################################################
    # function : get_my_blocked_friends
    # purpose : to get the logged in user's friend list
    # params : None
    # returns : friend list of the user
    # Exceptions : cypher.CypherError, cypher.CypherTransactionError
    ############################################################################
    def get_my_blocked_friends(self, u_sql_id):
        my_sql_id = u_sql_id
        print("hi")

        query = """
            MATCH (n:User)-[r:FRIENDS]-(n1:User)
            WHERE n1.sql_id = {sql_id}  and r.blocker_id = {blocker_id}
            return n
            ORDER BY n.givenName
        """

        try:
            friendlist = getGraphConnectionURI().cypher.execute(query, sql_id=my_sql_id, blocker_id=str(my_sql_id));

            return friendlist
        except cypher.CypherError, cypher.CypherTransactionError:
            raise "Exception occured in function get_my_blocked_friends"

    ############################################################################
    # function : get_user_by_email_id
    # purpose : function used to find user name based on sql_id
    # params : self (User), email_id
    # returns : User node
    # Exceptions : cypher.CypherError, cypher.CypherTransactionError
    ############################################################################
    def get_user_by_google_id(self, google_id):
        query = """
            MATCH (user:User)
            WHERE user.google_id = {google_id}
            RETURN user
        """
        try:
            regExPattern = google_id
            # user_profile = getGraphConnectionURI().find_one("User", "email", regExPattern)
            user_profile = getGraphConnectionURI().cypher.execute(query, google_id=google_id)
            return user_profile
        except cypher.CypherError, cypher.CypherTransactionError:
            raise "Exception occured in function get_user_by_google_id()"

            # END OF USER class


############################################################################
# function : get_all_recent_posts
# purpose : gets all posts from db
# params : None
# returns : set of usernames and posts
# Exceptions : cypher.CypherError, cypher.CypherTransactionError
############################################################################

def get_all_recent_posts(user_id):
    # query restricting for friends posts
    query = """
    MATCH (myself:User {sql_id:{sql_id}}), (user:User)-[:POSTED]->(post:Post)
    WHERE post.privacy = 'public' or (post.privacy = 'friends' and (user)-[:FRIENDS]-(myself))
    or (user.sql_id = myself.sql_id)
    OPTIONAL MATCH (post)-[:POSTED_TO]-(profile_user:User)
    RETURN user.displayName AS displayName, user, post, profile_user
    ORDER BY post.modified_time DESC
    """

    try:
        posts = getGraphConnectionURI().cypher.execute(query, {'sql_id': user_id})
        return posts
    except cypher.CypherError, cypher.CypherTransactionError:
        raise "Exception occured in function get_all_recent_posts "


############################################################################
# function : get_all_timeline_posts
# purpose : gets all posts posted in a timeline
# params : user_id
# returns : set of usernames and posts
# Exceptions : cypher.CypherError, cypher.CypherTransactionError
############################################################################
def get_all_profile_posts(user_id):
    query = """
    MATCH (myself:User {sql_id:{sql_id}}), (user:User)-[rel:POSTED]->(post:Post)
    WHERE (post)-[:POSTED_TO]-(myself) OR (not exists((post)-[:POSTED_TO]-()) AND (myself)-[rel]->(post))
    OPTIONAL MATCH (post)-[:HAS]->(comment:Comment), (commentedBy:User {sql_id: comment.user_sql_id})
    WITH post, rel, user, collect({post_id: post.id, comment: {id: comment.id, content: comment.content},
    user_sql_id: commentedBy.sql_id, displayName: commentedBy.displayName, image_url: commentedBy.image_url,
    google_id: commentedBy.google_id, creation_time: comment.creation_time }) as comments
    RETURN post, user, comments
    ORDER BY post.modified_time DESC
    """

    try:
        posts = getGraphConnectionURI().cypher.execute(query, {'sql_id': user_id})
        return posts
    except cypher.CypherError, cypher.CypherTransactionError:
        raise "Exception occured in function get_all_profile_posts"


############################################################################
# function : get_all_recent_comments
# purpose : gets all comments from db
# params : None
# returns : set of postids and set of comments
# Exceptions : cypher.CypherError, cypher.CypherTransactionError
############################################################################

def get_all_recent_comments():
    query = """
    MATCH (user:User),(post:Post)-[:HAS]->(comment:Comment)
    WHERE user.sql_id = comment.user_sql_id
    RETURN post.id AS postid, user, comment
    ORDER BY comment.creation_time
    """
    try:
        comments = getGraphConnectionURI().cypher.execute(query)
        return comments
    except cypher.CypherError, cypher.CypherTransactionError:
        raise "Exception occured in function get_all_recent_comments "


############################################################################
# function : get_total_likes_for_posts
# purpose : gets all likes from db
# params : None
# returns : set of postids and number of likes for all posts
# Exceptions : cypher.CypherError, cypher.CypherTransactionError
############################################################################
def get_total_likes_for_posts():
    query = """
    MATCH (u:User)-[r:LIKED]->(p:Post)
    RETURN p.id as postid, count(*) as likecount
    """
    try:
        totalLikes = getGraphConnectionURI().cypher.execute(query)
        return totalLikes
    except cypher.CypherError, cypher.CypherTransactionError:
        raise "Exception occured in function get_total_likes_for_posts"


############################################################################
# function : get_all_post_owners
# purpose : gets all posts and their owners from db
# params : None
# returns : set of postids and userid for all posts
# Exceptions : cypher.CypherError, cypher.CypherTransactionError
############################################################################
def get_all_post_owners():
    query = """
    MATCH (u:User)-[r:POSTED]->(p:Post)
    RETURN p.id as postid, u.sql_id as userid
    ORDER BY p.modified_time DESC
    """
    try:
        postOwners = getGraphConnectionURI().cypher.execute(query)
        return postOwners
    except cypher.CypherError, cypher.CypherTransactionError:
        raise "Exception occured in function get_all_post_owners "


############################################################################
# function : get_all_recent_likes
# purpose : gets all likes from db
# params : None
# returns : set of postids and userid who liked those posts
# Exceptions : cypher.CypherError, cypher.CypherTransactionError
############################################################################
def get_all_recent_likes():
    query = """
    MATCH (u:User)-[r:LIKED]->(p:Post)
    RETURN p.id as postid, u.sql_id as userid
    ORDER BY p.modified_time DESC
    """
    try:
        likes = getGraphConnectionURI().cypher.execute(query)
        return likes
    except cypher.CypherError, cypher.CypherTransactionError:
        raise "Exception occured in function get_all_recent_likes "


############################################################################
# function : timestamp
# purpose : convert the normal date time to milliseconds
# params : None
# returns : timestamp in milliseconds
# Exceptions : None
############################################################################

def timestamp():
    milliseconds = int(round(time.time() * 1000))
    return milliseconds


############################################################################
# function : convert_milliseconds_to_normal_date
# purpose : function to convert milliseconds to normal date time
# params : milliseconds
# returns : returns date
# Exceptions : None
############################################################################

def convert_milliseconds_to_normal_date(milliseconds):
    seconds = milliseconds / 1000.0
    normal_date_time = datetime.datetime.fromtimestamp(seconds).strftime('%m-%d-%Y %H:%M')
    return normal_date_time


############################################################################
# function : date
# purpose : function to return current date with given format
# params : None
# returns : returns current date in YYYY-DD-MM format
# Exceptions : None
############################################################################

def date():
    return datetime.datetime.now().strftime('%Y-%m-%d')


############################################################################
# function : get_sqlId
# purpose : function to return Sql Id of the user from Neo4j
# params : GoogleId
# returns : returns Sql Id
# Exceptions : cypher.CypherError, cypher.CypherTransactionError
############################################################################
def get_sqlId(google_id):
    query = """
        MATCH (user:User)
        WHERE user.google_id = {google_id}
        RETURN user.sql_id as sql_id
    """
    try:
        regExPattern = google_id
        # user_profile = getGraphConnectionURI().find_one("User", "email", regExPattern)
        sql_id = getGraphConnectionURI().cypher.execute(query, google_id=google_id)
        return sql_id
    except cypher.CypherError, cypher.CypherTransactionError:
        raise "Exception occured in function get_sqlId()"


############################################################################
# function : get_address_from_lat_lng
# purpose : function to convert latitude and longitude to human readable address via Google API
# params : latitude, longitude
# returns : returns address
# Exceptions : Exception
############################################################################

def get_address_from_lat_lng(latitude, longitude):
    try:
        address = ""
        geocodeAPIBaseURL = "https://maps.googleapis.com/maps/api/geocode/json?address="
        geocodeAPIURL = geocodeAPIBaseURL + str(latitude) + "," + str(longitude)
        google_api_response = requests.get(geocodeAPIURL)
        # For successful API call, response code will be 200 (OK)
        if(google_api_response.ok):
            jData = json.loads(google_api_response.content)
            if(len(jData['results']) > 0):
                address = jData['results'][0]['formatted_address']
        return address
    except Exception as e:
        print e
        raise "Exception occured in get_address_from_lat_lng " + str(e)


################################################################################
# Class : System
# Contains information related to the system
################################################################################

class System:
    ############################################################################
    # function : __init__
    # purpose : main function sets system_uid
    # params : None
    # returns : None
    # Exceptions : None
    ############################################################################

    def __init__(self):
        self.system_uid = None

    ############################################################################
    # function : find
    # purpose : function used to find user name based on sql_id
    # params : self (User)
    # returns : User node
    # Exceptions : cypher.CypherError, cypher.CypherTransactionError
    ############################################################################

    def find(self, system_uid):
        try:
            system = getGraphConnectionURI().find_one("System", "system_uid", system_uid)
            return system
        except cypher.CypherError, cypher.CypherTransactionError:
            raise "Exception occured in function User.find()"

    ############################################################################
    # function : get_system_post_owners
    # purpose : gets all likes from db
    # params : None
    # returns : set of postids and number of likes for all posts
    # Exceptions : cypher.CypherError, cypher.CypherTransactionError
    ############################################################################
    def get_system_post_owners(self, system_uid):
        query = """
        MATCH (u:User)-[r:USER_POSTED]->(p:SystemPost)<-[r2:SYS_POSTED]-(s:System)
        WHERE s.system_uid = {system_uid}
        RETURN p.id as postid, u.sql_id as userid
        ORDER BY p.modified_time DESC
        """
        try:
            likes = getGraphConnectionURI().cypher.execute(query, system_uid=system_uid)
            return likes
        except cypher.CypherError, cypher.CypherTransactionError:
            raise "Exception occured in function get_system_post_owners"

    ############################################################################
    # function : get_system_recent_likes
    # purpose : gets all likes from db
    # params : None
    # returns : set of postids and number of likes for all posts
    # Exceptions : cypher.CypherError, cypher.CypherTransactionError
    ############################################################################
    def get_system_recent_likes(self, system_uid):
        query = """

        MATCH (u:User)-[r:SYS_LIKED]->(p:SystemPost)<-[r1:SYS_POSTED]-(s:System)
        WHERE s.system_uid = {system_uid}
        RETURN p.id as postid, u.sql_id as userid
        ORDER BY p.modified_time DESC
        """
        try:
            likes = getGraphConnectionURI().cypher.execute(query, system_uid=system_uid)
            return likes
        except cypher.CypherError, cypher.CypherTransactionError:
            raise "Exception occured in function get_system_recent_likes"

    ############################################################################
    # function : get_total_likes_for_system_posts
    # purpose : gets all likes from db
    # params : None
    # returns : set of postids and number of likes for all posts
    # Exceptions : cypher.CypherError, cypher.CypherTransactionError
    ############################################################################
    def get_total_likes_for_system_posts(self, system_uid):
        query = """
        MATCH (u:User)-[r:SYS_LIKED]->(p:SystemPost)<-[r1:SYS_POSTED]-(s:System)
        WHERE s.system_uid = {system_uid}
        RETURN p.id as postid, count(*) as likecount
        """
        try:
            totalLikes = getGraphConnectionURI().cypher.execute(query, system_uid=system_uid)
            return totalLikes
        except cypher.CypherError, cypher.CypherTransactionError:
            raise "Exception occured in function get_total_likes_for_system_posts"

    ############################################################################
    # function : get_system_recent_posts
    # purpose : gets all posts from db
    # params : None
    # returns : set of usernames and posts
    # Exceptions : cypher.CypherError, cypher.CypherTransactionError
    ############################################################################

    def get_system_recent_posts(self, system_uid):
        query = """
        MATCH (system:System)-[r1:SYS_POSTED]->(post:SystemPost)<-[r2:USER_POSTED]-(user:User)
        WHERE system.system_uid = {system_uid}
        RETURN user.displayName AS displayName, user, post
        ORDER BY post.modified_time DESC
        """
        try:
            posts = getGraphConnectionURI().cypher.execute(query, system_uid=system_uid)
            return posts
        except cypher.CypherError, cypher.CypherTransactionError:
            raise "Exception occured in function get_system_recent_posts "

            ############################################################################

    # function : get_system_recent_comments
    # purpose : gets all system comments from db
    # params : system_uid : uid of system
    # returns : set of usernames and posts
    # Exceptions : cypher.CypherError, cypher.CypherTransactionError
    ############################################################################

    def get_system_recent_comments(self, system_uid):
        query = """
        MATCH (user:User), (system:System)-[r1:SYS_POSTED]->(post:SystemPost)-[r:HAS]->(comment:SystemComment)
        WHERE system.system_uid = {system_uid}
        and user.sql_id = comment.user_sql_id
        RETURN post.id AS postid, user, comment
        order by comment.creation_time
        """
        try:
            comments = getGraphConnectionURI().cypher.execute(query, system_uid=system_uid)
            return comments
        except cypher.CypherError, cypher.CypherTransactionError:
            raise "Exception occured in function get_system_recent_comments "

    ############################################################################
    # function : get_system_by_name
    # purpose : gets the system details for the matched system name from neo4j database
    # params : systemName
    # returns : system node(s)
    # Exceptions : cypher.CypherError, cypher.CypherTransactionError
    ############################################################################

    def get_system_by_name(self, systemName):
        query = """
            MATCH (system:System)
            WHERE system.name =~ {systemName}
            RETURN system
        """
        try:
            regExPattern = '(?i).*' + systemName + '.*'
            system_details = getGraphConnectionURI().cypher.execute(query, systemName=regExPattern)
            return system_details
        except cypher.CypherError, cypher.CypherTransactionError:
            raise "Exception occured in function get_system_by_name"

    ############################################################################
    # function : get_system_by_uid
    # purpose : gets the system details for the matched system_uid from neo4j database
    # params : system_uid
    # returns : system node
    # Exceptions : cypher.CypherError, cypher.CypherTransactionError
    ############################################################################

    def get_system_by_uid(self, system_uid):
        query = """
            MATCH (system:System)
            WHERE system.system_uid = {system_uid}
            RETURN system
        """
        try:
            system_neo4j = getGraphConnectionURI().cypher.execute(query, system_uid=system_uid)
            return system_neo4j
        except cypher.CypherError, cypher.CypherTransactionError:
            raise "Exception occured in function get_system_by_uid"

    ############################################################################
    # function : get_mysql_system_by_uid
    # purpose : gets the system details for the matched system_uid from mysql database
    # params : system_uid
    # returns : system node
    # Exceptions : cypher.CypherError, cypher.CypherTransactionError
    ############################################################################

    def get_mysql_system_by_uid(self, system_uid):
        try:
            # system_mysql =  getGraphConnectionURI().cypher.execute(query, system_uid = system_uid)
            # result = json.loads(response.data)
            system_mysql = "hello"
            return system_mysql
        except Exception as e:
            print str(e)
            raise "Exception occured in function get_mysql_system_by_uid()"

    ############################################################################
    # function : get_admin_systems
    # purpose : gets the system details where the specified user is admin for those systems from neo4j database
    # params : sql_id
    # returns : system node(s)
    # Exceptions : cypher.CypherError, cypher.CypherTransactionError
    ############################################################################

    def get_admin_systems(self, sql_id):
        query = """
            MATCH (user:User)-[:SYS_ADMIN]->(system:System)
            WHERE user.sql_id = {sql_id}
            RETURN system
            ORDER BY system.name
        """
        try:
            admin_systems = getGraphConnectionURI().cypher.execute(query, sql_id=sql_id)
            return admin_systems
        except cypher.CypherError, cypher.CypherTransactionError:
            raise "Exception occured in function get_admin_systems"

    ############################################################################
    # function : get_system_admins
    # purpose : gets the admin detail for the provided system_uid from neo4j database
    # params : system_uid
    # returns : user node(s)
    # Exceptions : cypher.CypherError, cypher.CypherTransactionError
    ############################################################################
    def get_system_admins(self, system_uid):
        query = """
            MATCH (user:User)-[rel:SYS_ADMIN]->(sys:System)
            WHERE sys.system_uid = {system_uid}
            return user, count(*) as total_admins
            ORDER BY user.givenName
        """
        try:
            system_admins = getGraphConnectionURI().cypher.execute(query, system_uid=system_uid)
            return system_admins
        except cypher.CypherError, cypher.CypherTransactionError:
            raise "Exception occured in function get_system_admins"

    ############################################################################
    # function : get_participated_systems
    # purpose : gets the system details where the user has participated for ; from neo4j database
    # params : sql_id
    # returns : system node(s)
    # Exceptions : cypher.CypherError, cypher.CypherTransactionError
    ############################################################################

    def get_participated_systems(self, sql_id):
        query = """
            MATCH (user:User)-[:SYS_PARTICIPANT]->(system:System)
            WHERE user.sql_id = {sql_id}
            RETURN system
            ORDER BY system.name
        """
        try:
            participated_systems = getGraphConnectionURI().cypher.execute(query, sql_id=sql_id)
            return participated_systems
        except cypher.CypherError, cypher.CypherTransactionError:
            raise "Exception occured in function get_participated_systems"

    ############################################################################
    # function : get_user_privilege_for_system
    # purpose : gets the user privilege (based on logged in user) for the provided system_uid from neo4j database
    # params : sql_id, system_uid
    # returns : user_privilege
    # Exceptions : cypher.CypherError, cypher.CypherTransactionError
    ############################################################################
    def get_user_privilege_for_system(self, sql_id, system_uid):
        user_privilege = None
        query = """
             match (user:User)-[r]->(system:System)
             WHERE user.sql_id = {sql_id} and system.system_uid = {system_uid}
             return type(r) as rel_type
        """
        try:
            relationship_type = getGraphConnectionURI().cypher.execute(query, sql_id=sql_id, system_uid=system_uid)
            if not relationship_type:
                user_privilege = None
            else:
                rel_type = relationship_type[0]['rel_type']
                if (rel_type == "SYS_ADMIN"):
                    user_privilege = "SYS_ADMIN"
                elif (rel_type == "SYS_PARTICIPANT"):
                    user_privilege = "SYS_PARTICIPANT"
                elif (rel_type == "SYS_SUBSCRIBER"):
                    user_privilege = "SYS_SUBSCRIBER"
                elif (rel_type == "SYS_PENDING_PARTICIPANT"):
                    user_privilege = "SYS_PENDING_PARTICIPANT"
                elif (rel_type == "SYS_PENDING_SUBSCRIBER"):
                    user_privilege = "SYS_PENDING_SUBSCRIBER"
            return user_privilege
        except cypher.CypherError, cypher.CypherTransactionError:
            raise "Exception occured in function get_user_privilege_for_system"

    ############################################################################
    # function : approve_system_participant
    # purpose : Approve the participant request of the specified user for the provided system_uid
    # params : google_id, system_uid
    # returns : None
    # Exceptions : cypher.CypherError, cypher.CypherTransactionError
    ############################################################################
    def approve_system_participant(self, google_id, system_uid):
        removeRelationshipQuery = """
                MATCH (u:User)-[rel:SYS_PENDING_PARTICIPANT]->(s:System)
                WHERE u.google_id = {google_id} and s.system_uid={system_uid}
                DETACH DELETE rel
        """
        createRelationshipQuery = """
                MATCH (u:User), (s:System)
                WHERE u.google_id = {google_id} and s.system_uid={system_uid}
                CREATE UNIQUE (u)-[rel:SYS_PARTICIPANT]->(s)
                RETURN rel
        """
        try:
            remove_relationship_status = getGraphConnectionURI().cypher.execute(removeRelationshipQuery,
                                                                                google_id=google_id,
                                                                                system_uid=system_uid)
            create_relationship_status = getGraphConnectionURI().cypher.execute(createRelationshipQuery,
                                                                                google_id=google_id,
                                                                                system_uid=system_uid)
        except cypher.CypherError, cypher.CypherTransactionError:
            raise "Exception occured in function approve_system_participant"

    ############################################################################
    # function : reject_system_participant
    # purpose : Reject the participant request of the specified user for the provided system_uid
    # params : google_id, system_uid
    # returns : None
    # Exceptions : cypher.CypherError, cypher.CypherTransactionError
    ############################################################################
    def reject_system_participant(self, google_id, system_uid):
        removeRelationshipQuery = """
                MATCH (u:User)-[rel:SYS_PENDING_PARTICIPANT]->(s:System)
                WHERE u.google_id = {google_id} and s.system_uid={system_uid}
                DETACH DELETE rel
        """
        try:
            remove_relationship_status = getGraphConnectionURI().cypher.execute(removeRelationshipQuery,
                                                                                google_id=google_id,
                                                                                system_uid=system_uid)
        except cypher.CypherError, cypher.CypherTransactionError:
            raise "Exception occured in function reject_system_participant"

    ############################################################################
    # function : pending_subscribe_to_system
    # purpose : When the user clicks on "Subscribe" button in the systems page, SYS_PENDING_SUBSCRIBER relationship
    # is created between the user and system node
    # params : google_id, system_uid
    # returns : None
    # Exceptions : cypher.CypherError, cypher.CypherTransactionError
    ############################################################################
    def pending_subscribe_to_system(self, google_id, system_uid):
        removeRelationshipQuery = """
                MATCH (u:User)-[rel]->(s:System)
                WHERE u.google_id = {google_id} and s.system_uid={system_uid}
                DETACH DELETE rel
        """
        createPendingSubscribeRelationshipQuery = """
                MATCH (u:User), (s:System)
                WHERE u.google_id = {google_id} and s.system_uid={system_uid}
                CREATE UNIQUE (u)-[rel:SYS_PENDING_SUBSCRIBER]->(s)
                RETURN rel
        """
        try:
            remove_relationship_status = getGraphConnectionURI().cypher.execute(removeRelationshipQuery,
                                                                                google_id=google_id,
                                                                                system_uid=system_uid)
            create_relationship_status = getGraphConnectionURI().cypher.execute(createPendingSubscribeRelationshipQuery,
                                                                                google_id=google_id,
                                                                                system_uid=system_uid)
        except cypher.CypherError, cypher.CypherTransactionError:
            raise "Exception occured in function pending_subscribe_to_system"

    ############################################################################
    # function : subscribe_to_system
    # purpose : When the user clicks on "Subscribe" button in the systems page, SYS_SUBSCRIBER relationship
    # is created between the user and system node
    # params : google_id, system_uid
    # returns : None
    # Exceptions : cypher.CypherError, cypher.CypherTransactionError
    ############################################################################
    def subscribe_to_system(self, google_id, system_uid):
        removeRelationshipQuery = """
                MATCH (u:User)-[rel]->(s:System)
                WHERE u.google_id = {google_id} and s.system_uid={system_uid}
                DETACH DELETE rel
        """
        createSubscribeRelationshipQuery = """
                MATCH (u:User), (s:System)
                WHERE u.google_id = {google_id} and s.system_uid={system_uid}
                CREATE UNIQUE (u)-[rel:SYS_SUBSCRIBER]->(s)
                RETURN rel
        """
        try:
            remove_relationship_status = getGraphConnectionURI().cypher.execute(removeRelationshipQuery,
                                                                                google_id=google_id,
                                                                                system_uid=system_uid)
            create_relationship_status = getGraphConnectionURI().cypher.execute(createSubscribeRelationshipQuery,
                                                                                google_id=google_id,
                                                                                system_uid=system_uid)
        except cypher.CypherError, cypher.CypherTransactionError:
            raise "Exception occured in function subscribe_to_system"

    ############################################################################
    # function : pending_participate_to_system
    # purpose : When the user clicks on "Participate" button in the systems page, SYS_PENDING_PARTICIPANT relationship
    # is created between the user and system node
    # params : google_id, system_uid
    # returns : None
    # Exceptions : cypher.CypherError, cypher.CypherTransactionError
    ############################################################################
    def pending_participate_to_system(self, google_id, system_uid):
        removeRelationshipQuery = """
                MATCH (u:User)-[rel]->(s:System)
                WHERE u.google_id = {google_id} and s.system_uid={system_uid}
                DETACH DELETE rel
        """
        createPendingParticipateRelationshipQuery = """
                MATCH (u:User), (s:System)
                WHERE u.google_id = {google_id} and s.system_uid={system_uid}
                CREATE UNIQUE (u)-[rel:SYS_PENDING_PARTICIPANT]->(s)
                RETURN rel
        """
        try:
            remove_relationship_status = getGraphConnectionURI().cypher.execute(removeRelationshipQuery,
                                                                                google_id=google_id,
                                                                                system_uid=system_uid)
            create_relationship_status = getGraphConnectionURI().cypher.execute(
                createPendingParticipateRelationshipQuery,
                google_id=google_id,
                system_uid=system_uid)
        except cypher.CypherError, cypher.CypherTransactionError:
            raise "Exception occured in function pending_participate_to_system"

    ############################################################################
    # function : leave_system
    # purpose : When the user leaves the system, we remove the relationship associated between user and system node
    # params : google_id, system_uid
    # returns : None
    # Exceptions : cypher.CypherError, cypher.CypherTransactionError
    ############################################################################
    def leave_system(self, google_id, system_uid):
        removeRelationshipQuery = """
                MATCH (u:User)-[rel]->(s:System)
                WHERE u.google_id = {google_id} and s.system_uid={system_uid}
                DETACH DELETE rel
        """
        try:
            remove_relationship_status = getGraphConnectionURI().cypher.execute(removeRelationshipQuery,
                                                                                google_id=google_id,
                                                                                system_uid=system_uid)
        except cypher.CypherError, cypher.CypherTransactionError:
            raise "Exception occured in function leave_system"

    ############################################################################
    # function : delete_system_participant
    # purpose : Delete the relationship of the specified participant with the system node (SYS_PARTICIPANT)
    # params : google_id, system_uid
    # returns : None
    # Exceptions : cypher.CypherError, cypher.CypherTransactionError
    ############################################################################
    def delete_system_participant(self, google_id, system_uid):
        removeRelationshipQuery = """
                MATCH (u:User)-[rel:SYS_PARTICIPANT]->(s:System)
                WHERE u.google_id = {google_id} and s.system_uid={system_uid}
                DETACH DELETE rel
        """
        try:
            remove_relationship_status = getGraphConnectionURI().cypher.execute(removeRelationshipQuery,
                                                                                google_id=google_id,
                                                                                system_uid=system_uid)
        except cypher.CypherError, cypher.CypherTransactionError:
            raise "Exception occured in function delete_system_participant"

    ############################################################################
    # function : make_admin_for_system
    # purpose : Add the user as admin of the specified system (SYS_ADMIN)
    # params : google_id, system_uid
    # returns : None
    # Exceptions : cypher.CypherError, cypher.CypherTransactionError
    ############################################################################
    def make_admin_for_system(self, google_id, system_uid):
        removeRelationshipQuery = """
                MATCH (u:User)-[rel]->(s:System)
                WHERE u.google_id = {google_id} and s.system_uid={system_uid}
                DETACH DELETE rel
        """
        createAdminRelationshipQuery = """
                MATCH (u:User), (s:System)
                WHERE u.google_id = {google_id} and s.system_uid={system_uid}
                CREATE UNIQUE (u)-[rel:SYS_ADMIN]->(s)
                RETURN rel
        """
        try:
            remove_relationship_status = getGraphConnectionURI().cypher.execute(removeRelationshipQuery,
                                                                                google_id=google_id,
                                                                                system_uid=system_uid)
            create_relationship_status = getGraphConnectionURI().cypher.execute(createAdminRelationshipQuery,
                                                                                google_id=google_id,
                                                                                system_uid=system_uid)
        except cypher.CypherError, cypher.CypherTransactionError:
            raise "Exception occured in function make_admin_for_system"

    ############################################################################
    # function : make_participant_for_system
    # purpose : Add the user as subscriber of the specified system (SYS_PARTICIPANT)
    # params : google_id, system_uid
    # returns : None
    # Exceptions : cypher.CypherError, cypher.CypherTransactionError
    ############################################################################
    def make_participant_for_system(self, google_id, system_uid):
        removeRelationshipQuery = """
                MATCH (u:User)-[rel]->(s:System)
                WHERE u.google_id = {google_id} and s.system_uid={system_uid}
                DETACH DELETE rel
        """
        createParticipantRelationshipQuery = """
                MATCH (u:User), (s:System)
                WHERE u.google_id = {google_id} and s.system_uid={system_uid}
                CREATE UNIQUE (u)-[rel:SYS_PARTICIPANT]->(s)
                RETURN rel
        """
        try:
            remove_relationship_status = getGraphConnectionURI().cypher.execute(removeRelationshipQuery,
                                                                                google_id=google_id,
                                                                                system_uid=system_uid)
            create_relationship_status = getGraphConnectionURI().cypher.execute(createParticipantRelationshipQuery,
                                                                                google_id=google_id,
                                                                                system_uid=system_uid)
        except cypher.CypherError, cypher.CypherTransactionError:
            raise "Exception occured in function make_participant_for_system"

    ############################################################################
    # function : make_subscriber_for_system
    # purpose : Add the user as subscriber of the specified system (SYS_SUBSCRIBER)
    # params : google_id, system_uid
    # returns : None
    # Exceptions : cypher.CypherError, cypher.CypherTransactionError
    ############################################################################
    def make_subscriber_for_system(self, google_id, system_uid):
        removeRelationshipQuery = """
                MATCH (u:User)-[rel]->(s:System)
                WHERE u.google_id = {google_id} and s.system_uid={system_uid}
                DETACH DELETE rel
        """
        createSubscriberRelationshipQuery = """
                MATCH (u:User), (s:System)
                WHERE u.google_id = {google_id} and s.system_uid={system_uid}
                CREATE UNIQUE (u)-[rel:SYS_SUBSCRIBER]->(s)
                RETURN rel
        """
        try:
            remove_relationship_status = getGraphConnectionURI().cypher.execute(removeRelationshipQuery,
                                                                                google_id=google_id,
                                                                                system_uid=system_uid)
            create_relationship_status = getGraphConnectionURI().cypher.execute(createSubscriberRelationshipQuery,
                                                                                google_id=google_id,
                                                                                system_uid=system_uid)
        except cypher.CypherError, cypher.CypherTransactionError:
            raise "Exception occured in function make_subscriber_for_system"

    ############################################################################
    # function : delete_system_admin
    # purpose : Delete the relationship of the specified participant with the system node (SYS_ADMIN)
    # params : google_id, system_uid
    # returns : None
    # Exceptions : cypher.CypherError, cypher.CypherTransactionError
    ############################################################################
    def delete_system_admin(self, google_id, system_uid):
        removeRelationshipQuery = """
                MATCH (u:User)-[rel:SYS_ADMIN]->(s:System)
                WHERE u.google_id = {google_id} and s.system_uid={system_uid}
                DETACH DELETE rel
        """
        try:
            remove_relationship_status = getGraphConnectionURI().cypher.execute(removeRelationshipQuery,
                                                                                google_id=google_id,
                                                                                system_uid=system_uid)
        except cypher.CypherError, cypher.CypherTransactionError:
            raise "Exception occured in function delete_system_admin"

    ############################################################################
    # function : delete_system_subscriber
    # purpose : Delete the relationship of the specified participant with the system node (SYS_SUBSCRIBER)
    # params : google_id, system_uid
    # returns : None
    # Exceptions : cypher.CypherError, cypher.CypherTransactionError
    ############################################################################
    def delete_system_subscriber(self, google_id, system_uid):
        removeRelationshipQuery = """
                MATCH (u:User)-[rel:SYS_SUBSCRIBER]->(s:System)
                WHERE u.google_id = {google_id} and s.system_uid={system_uid}
                DETACH DELETE rel
        """
        try:
            remove_relationship_status = getGraphConnectionURI().cypher.execute(removeRelationshipQuery,
                                                                                google_id=google_id,
                                                                                system_uid=system_uid)
        except cypher.CypherError, cypher.CypherTransactionError:
            raise "Exception occured in function delete_system_subscriber"

    ############################################################################
    # function : get_system_participants
    # purpose : gets the participant detail for the provided system_uid from neo4j database
    # params : system_uid
    # returns : user node(s)
    # Exceptions : cypher.CypherError, cypher.CypherTransactionError
    ############################################################################
    def get_system_participants(self, system_uid):
        query = """
            MATCH (user:User)-[rel:SYS_PARTICIPANT]->(sys:System)
            WHERE sys.system_uid = {system_uid}
            return user as participants
            ORDER BY user.givenName
        """
        try:
            system_participants = getGraphConnectionURI().cypher.execute(query, system_uid=system_uid)
            return system_participants
        except cypher.CypherError, cypher.CypherTransactionError:
            raise "Exception occured in function get_system_participants"

    ############################################################################
    # function : get_participants_pending_approval
    # purpose : gets the participant details whose approval to join the system is pending by the administrator
    # params : system_uid
    # returns : user node(s)
    # Exceptions : cypher.CypherError, cypher.CypherTransactionError
    ############################################################################
    def get_participants_pending_approval(self, system_uid):
        query = """
            MATCH (user:User)-[rel:SYS_PENDING_PARTICIPANT]->(sys:System)
            WHERE sys.system_uid = {system_uid}
            return user as pending_participants
            ORDER BY user.givenName
        """
        try:
            participants_pending_approval = getGraphConnectionURI().cypher.execute(query, system_uid=system_uid)
            return participants_pending_approval
        except cypher.CypherError, cypher.CypherTransactionError:
            raise "Exception occured in function get_participants_pending_approval"

    ############################################################################
    # function : subscribed_systems
    # purpose : gets the system details where the user has subscribed for ; from neo4j database
    # params : sql_id
    # returns : system node(s)
    # Exceptions : cypher.CypherError, cypher.CypherTransactionError
    ############################################################################

    def get_subscribed_systems(self, sql_id):
        query = """
            MATCH (user:User)-[:SYS_SUBSCRIBER]->(system:System)
            WHERE user.sql_id = {sql_id}
            RETURN system
            ORDER BY system.name
        """
        try:
            subscribed_systems = getGraphConnectionURI().cypher.execute(query, sql_id=sql_id)
            return subscribed_systems
        except cypher.CypherError, cypher.CypherTransactionError:
            raise "Exception occured in function get_subscribed_systems"

    ############################################################################
    # function : get_system_subscribers
    # purpose : gets the subscriber detail for the provided system_uid from neo4j database
    # params : system_uid
    # returns : user node(s)
    # Exceptions : cypher.CypherError, cypher.CypherTransactionError
    ############################################################################
    def get_system_subscribers(self, system_uid):
        query = """
            MATCH (user:User)-[rel:SYS_SUBSCRIBER]->(sys:System)
            WHERE sys.system_uid = {system_uid}
            return user as subscriber
            ORDER BY user.givenName
        """
        try:
            system_subscribers = getGraphConnectionURI().cypher.execute(query, system_uid=system_uid)
            return system_subscribers
        except cypher.CypherError, cypher.CypherTransactionError:
            raise "Exception occured in function get_system_subscribers"

    ############################################################################
    # function : get_subscribers_pending_approval
    # purpose : gets the subscriber details whose approval to join the system is pending by the administrator
    # params : system_uid
    # returns : user node(s)
    # Exceptions : cypher.CypherError, cypher.CypherTransactionError
    ############################################################################
    def get_subscribers_pending_approval(self, system_uid):
        query = """
            MATCH (user:User)-[rel:SYS_PENDING_SUBSCRIBER]->(sys:System)
            WHERE sys.system_uid = {system_uid}
            return user as pending_subscribers
            ORDER BY user.givenName
        """
        try:
            subscribers_pending_approval = getGraphConnectionURI().cypher.execute(query, system_uid=system_uid)
            return subscribers_pending_approval
        except cypher.CypherError, cypher.CypherTransactionError:
            raise "Exception occured in function get_subscribers_pending_approval"

    ############################################################################
    # function : get_recommended_systems
    # purpose : gets the recommended system details for the specified user from neo4j database
    # params : sql_id
    # returns : system node(s)
    # Exceptions : cypher.CypherError, cypher.CypherTransactionError
    ############################################################################
    def get_recommended_systems(self, sql_id):
        friends_system_query = """
            MATCH (friend:User)-[rel]->(system:System),
            (mySelf:User)
            where mySelf.sql_id = {sql_id} and
            NOT (mySelf)-[:SYS_PARTICIPANT]-(system) and
            NOT (mySelf)-[:SYS_ADMIN]-(system) and
            NOT (mySelf)-[:SYS_SUBSCRIBER]-(system) and
            (mySelf)-[:FRIENDS]-(friend)
            return friend, system
            ORDER By friend.givenName
        """
        try:
            # Minimum Depth Level To Identify The Recommended Systems
            minimum_depth_level = 2;
            friends_system = getGraphConnectionURI().cypher.execute(friends_system_query, sql_id=sql_id)
            mutual_system_between_friends = System().get_mutual_system_between_friends(friends_system,
                                                                                       minimum_depth_level)
            return mutual_system_between_friends
        except cypher.CypherError, cypher.CypherTransactionError:
            raise "Exception occured in function get_recommended_systems"

    ############################################################################
    # function : add_system_post
    # purpose : adds post related to a system with user_id and post content in neo4j database
    # params : system_uid, user_sql_id, text, privacy, link
    # returns : None
    # Exceptions : cypher.CypherError, cypher.CypherTransactionError
    ############################################################################
    def add_system_post(self, system_uid, user_sql_id, text, privacy, link):
        systemnew = System().find(system_uid)
        print(systemnew)
        user = User(user_sql_id).find()
        post = Node(
            "SystemPost",
            id=str(uuid.uuid4()),
            text=text,
            link=link,
            privacy=privacy,
            userid=user_sql_id,
            creation_time=timestamp(),
            modified_time=timestamp(),
            date=date()
        )
        sys_syspost_relationship = Relationship(systemnew, "SYS_POSTED", post)
        user_syspost_relationship = Relationship(user, "USER_POSTED", post)
        try:
            getGraphConnectionURI().create(sys_syspost_relationship)
            getGraphConnectionURI().create(user_syspost_relationship)
        except cypher.CypherError, cypher.CypherTransactionError:
            raise "Exception occured in function add_system_post "

    ############################################################################
    # function : delete_system_comment
    # purpose : deletes system comment node in neo4j with the given id
    # params :
    #        commentid : comment id which is being added
    # Exceptions : cypher.CypherError, cypher.CypherTransactionError
    # returns : None
    ############################################################################

    def delete_system_comment(self, commentid):
        print("Comment id" + str(commentid))
        query = """
        MATCH (comment:SystemComment)
        WHERE comment.id = {commentid}
        DETACH DELETE comment
        """
        try:
            getGraphConnectionURI().cypher.execute(query, commentid=commentid);
        except cypher.CypherError, cypher.CypherTransactionError:
            raise "Exception occured in function delete_system_comment "

    ############################################################################
    # function : edit_system_comment
    # purpose : Edits comment node in neo4j with the given id
    # params :
    #        newcomment : contains the data shared in comment
    #        commentid : comment id which is being added
    # Exceptions : cypher.CypherError, cypher.CypherTransactionError
    # returns : None
    ############################################################################

    def edit_system_comment(self, newcomment, commentid):
        print(commentid)
        query = """
        MATCH (comment:SystemComment)
        WHERE comment.id = {commentid}
        SET comment.content = {newcomment}
        RETURN comment
        """
        try:
            getGraphConnectionURI().cypher.execute(query, commentid=commentid, newcomment=newcomment);
        except cypher.CypherError, cypher.CypherTransactionError:
            raise "Exception occured in function edit_system_comment"

    ############################################################################
    # function : edit_system_post
    # purpose : Edits post node in neo4j with the given id
    # params :
    #        newcontent : contains the data shared in comment
    #        postid : comment id which is being added
    # Exceptions : cypher.CypherError, cypher.CypherTransactionError
    # returns : None
    ############################################################################

    def edit_system_post(self, newcontent, postid):
        query = """
        MATCH (post:SystemPost)
        WHERE post.id = {postid}
        SET post.text = {newcontent}
        RETURN post
        """
        try:
            getGraphConnectionURI().cypher.execute(query, postid=postid, newcontent=newcontent);
        except cypher.CypherError, cypher.CypherTransactionError:
            raise "Exception occured in function edit_system_post"

    ############################################################################
    # function : delete_system_post
    # purpose : deletes comments and all related relationships first
    #           and then deletes post and all relationships
    # params :
    #        postid : post id for which user liked
    # returns : None
    # Exceptions : cypher.CypherError, cypher.CypherTransactionError
    ############################################################################

    def delete_system_post(self, postid):
        post = getGraphConnectionURI().find_one("Post", "id", postid)

        # Deletes comments and all related relationships

        deleteSystemCommentsQuery = """
            MATCH (post:SystemPost)-[r:HAS]->(comment:SystemComment)
            WHERE post.id= {postid}
            DETACH DELETE comment
            """
        try:
            getGraphConnectionURI().cypher.execute(deleteSystemCommentsQuery, postid=postid)
        except cypher.CypherError, cypher.CypherTransactionError:
            raise "Exception occured in function delete_system_post : deleteSystemCommentsQuery "

        # Deletes posts and all related relationships

        deleteSystemPostQuery = """
            MATCH (post:SystemPost)
            WHERE post.id= {postid}
            DETACH DELETE post
            """
        try:
            getGraphConnectionURI().cypher.execute(deleteSystemPostQuery, postid=postid)
        except cypher.CypherError, cypher.CypherTransactionError:
            raise "Exception occured in function delete_system_post :deleteSystemPostQuery "

    ############################################################################
    # function : like_system_post
    # purpose : creates a unique LIKED relationship between User and Post
    # params : user_sql_id : user id
    #        system_postid : post id for which user liked
    # returns : None
    # Exceptions : cypher.CypherError, cypher.CypherTransactionError
    ############################################################################

    def like_system_post(self, user_sql_id, system_postid):
        user = User(user_sql_id).find()
        post = getGraphConnectionURI().find_one("SystemPost", "id", system_postid)
        rel = Relationship(user, 'SYS_LIKED', post)
        try:
            getGraphConnectionURI().create_unique(rel)
        except cypher.CypherError, cypher.CypherTransactionError:
            raise "Exception occured in function like_post "

    ############################################################################
    # function : add_system_comment
    # purpose : Adds new comment node in neo4j with the given information and creates
    #            POSTED relationship between Post and User node
    # params :
    #        newcomment : contains the data shared in comment
    #        postid : post id for which the comment has been added
    # Exceptions : cypher.CypherError, cypher.CypherTransactionError
    # returns : None
    ############################################################################

    def add_system_comment(self, user_sql_id, newcomment, system_postid):
        user = User(user_sql_id).find()
        post = getGraphConnectionURI().find_one("SystemPost", "id", system_postid)
        print(user)
        comment = Node(
            "SystemComment",
            id=str(uuid.uuid4()),
            content=newcomment,
            user_sql_id=user_sql_id,
            user_display_name=user['displayName'],
            creation_time=timestamp(),
            modified_time=timestamp())
        rel = Relationship(post, 'HAS', comment)
        try:
            getGraphConnectionURI().create(rel)
        except cypher.CypherError, cypher.CypherTransactionError:
            raise "Exception occured in function add_system_comment "

    ############################################################################
    # function : unlike_post
    # purpose : removes LIKED relationship between User and Post
    # params :
    #        postid : post id for which user liked
    # returns : None
    # Exceptions : cypher.CypherError, cypher.CypherTransactionError
    ############################################################################

    def unlike_system_post(self, user_sql_id, system_postid):
        user = User(user_sql_id).find()
        post = getGraphConnectionURI().find_one("SystemPost", "id", system_postid)
        query = """
            MATCH (u:User)-[r:SYS_LIKED]->(p:SystemPost)
            WHERE p.id= {postid} and u.sql_id = {userSqlId}
            DELETE r
        """
        try:
            getGraphConnectionURI().cypher.execute(query, postid=system_postid, userSqlId=user_sql_id);
        except cypher.CypherError, cypher.CypherTransactionError:
            raise "Exception occured in function get_search_friends"

    ############################################################################
    # function : get_mutual_system_between_friends
    # purpose : gets the mutual system between friends from neo4j database
    # params : Row(s) containing friend and his/her system, minimum_depth_level
    # returns : List of Mutual Systems Between Friends Of The User
    # Exceptions : cypher.CypherError, cypher.CypherTransactionError
    ############################################################################
    def get_mutual_system_between_friends(self, friends_system, minimum_depth_level):
        try:
            # Initial Dictionary to hold the mutual Systems between friend(s) For Processing
            list_of_mutual_systems_raw = {}
            # Dictionary to hold the mutual Systems between friend(s) - Depth Level 2
            list_of_mutual_systems = {}
            for each_friend_system in friends_system:
                friend = each_friend_system['friend']
                system = each_friend_system['system']
                system_uid = system['system_uid']
                # Do nothing when there exists no system_uid in the System node of Neo4J Database
                if system_uid is not None:
                    # If the key already exists, increment the occurrence by 1
                    if list_of_mutual_systems_raw.has_key(system_uid):
                        system_occurrence = list_of_mutual_systems_raw[system_uid]
                        system_occurrence += 1
                        list_of_mutual_systems_raw[system_uid] = system_occurrence
                    # If the key does not exists, set the occurrence to 1
                    else:
                        system_occurrence = 1
                        list_of_mutual_systems_raw[system_uid] = system_occurrence
            # Add the system_uid to dictionary only when the depth level is met
            for system_uid in list_of_mutual_systems_raw.keys():
                system_occurrence = list_of_mutual_systems_raw[system_uid]
                if system_occurrence >= minimum_depth_level:
                    list_of_mutual_systems[system_uid] = system_occurrence
            # Query to fetch the systems
            system_query = """
                MATCH (system:System)
                where system.system_uid IN {system_uid_collection}
                return system
                ORDER By system.name
            """
            mutual_system_between_friends = getGraphConnectionURI().cypher.execute(system_query,
                                                                                   system_uid_collection=list_of_mutual_systems.keys())
            return mutual_system_between_friends
        except cypher.CypherError, cypher.CypherTransactionError:
            raise "Exception occured in function get_mutual_system_between_friends"

    ############################################################################
    # function : get_all_systems
    # purpose : gets all the system that is present in the Neo4J database
    # params : None
    # returns : system node(s)
    # Exceptions : cypher.CypherError, cypher.CypherTransactionError
    ############################################################################

    def get_all_systems(self):
        query = """
            MATCH (system:System)
            RETURN system
            ORDER BY system.name
        """
        try:
            recommended_systems = getGraphConnectionURI().cypher.execute(query)
            return recommended_systems
        except cypher.CypherError, cypher.CypherTransactionError:

            raise "Exception occured in function get_all_systems"

        raise "Exception occured in function get_all_systems"


################################################################################
# Class : Privacy
# Contains the privacy information, such as default privacy and privacy options
# Defining Privacy enumeration in a simple way to avoiding extra dependencies
################################################################################
class Privacy:
    # Constants Definition
    # Privacy Options
    FRIENDS = "Friends"
    PRIVATE = "Private"
    PUBLIC = "Public"
    PARTICIPANTS = "Participants"  # Participants Only
    SUBSCRIBERS = "Subscribers"  # Participants and Subscribers
    ANYONE = "Anyone"  # Anyone is approved by default
    ADMIN_APPROVAL = "Approval"  # Needs to be approved by Admin
    SPECIFIED = "Specified"  # Defined per post by User

    ############################################################################
    # function : __init__
    # purpose : main function sets default privacy and possible privacy options
    # params :
    #       privacy_options, default_privacy
    # returns : None
    # Exceptions : None
    ############################################################################
    def __init__(self, privacy_options, default_privacy, page_type, page_id):
        self.privacy_options = privacy_options
        self.default_privacy = default_privacy
        self.page_type = page_type
        self.page_id = page_id
        self.user_relation = Privacy.PUBLIC
