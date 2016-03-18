from py2neo import Graph, Node, Relationship, cypher
import time
import datetime
import uuid


# Initialize the app_instance and graph_instance
def init_sc_app(app):
    global app_instance
    global graph_instance
    app_instance = app
    graph_instance = Graph(get_app_instance().config['CONNECTIONSETTING'])


# Return the app_instance
def get_app_instance():
    return app_instance


# Create / Load graph with the connection settings
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

    def add_post(self, text, privacy, link):
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
        rel = Relationship(user, "POSTED", post)
        try:
            getGraphConnectionURI().create(rel)
        except cypher.CypherError, cypher.CypherTransactionError:
            raise "Exception occured in function add_post "

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
            raise "Exception occured in function like_post : deleteCommentsQuery "

        # Deletes posts and all related relationships

        deletePostQuery = """
            MATCH (post:Post)
            WHERE post.id= {postid}
            DETACH DELETE post
            """
        try:
            getGraphConnectionURI().cypher.execute(deletePostQuery, postid=postid)
        except cypher.CypherError, cypher.CypherTransactionError:
            raise "Exception occured in function like_post : deletePostQuery "

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
        post = getGraphConnectionURI().find_one("Post", "id", postid)
        rel = Relationship(post, 'HAS', comment)
        try:
            getGraphConnectionURI().create(rel)
        except cypher.CypherError, cypher.CypherTransactionError:
            raise "Exception occured in function add_comment "

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

    def add_post(self, text, privacy, link):
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
        rel = Relationship(user, "POSTED", post)
        try:
            getGraphConnectionURI().create(rel)
        except cypher.CypherError, cypher.CypherTransactionError:
            raise "Exception occured in function add_post "

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
    # purpose : used when adding friends to return list of friends and list of users
    #           of currently logged in user
    # params : None
    # returns :
    # Exceptions : cypher.CypherError, cypher.CypherTransactionError
    ############################################################################
    def get_friends_and_sentreq(self):
        my_sql_id = self.sql_id
        my_sentreq_query = "MATCH (sentrequests { sql_id:{sql_id} })-[:SentRequest]->(res) RETURN res.sql_id"
        my_friends_query = "MATCH (friends { sql_id:{sql_id} })-[:FRIENDS]->(res) RETURN res.sql_id"

        try:
            sentreq_res = getGraphConnectionURI().cypher.execute(my_sentreq_query, sql_id=my_sql_id);
            frnds_res = getGraphConnectionURI().cypher.execute(my_friends_query, sql_id=my_sql_id);
            return sentreq_res, frnds_res
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

def get_all_recent_posts():
    query = """
    MATCH (user:User)-[:POSTED]->(post:Post)
    RETURN user.displayName AS displayName, post
    ORDER BY post.modified_time DESC
    """
    try:
        posts = getGraphConnectionURI().cypher.execute(query)
        return posts
    except cypher.CypherError, cypher.CypherTransactionError:
        raise "Exception occured in function get_all_recent_posts "


############################################################################
# function : get_all_recent_comments
# purpose : gets all comments from db
# params : None
# returns : set of postids and set of comments
# Exceptions : cypher.CypherError, cypher.CypherTransactionError
############################################################################

def get_all_recent_comments():
    query = """
    MATCH (post:Post)-[:HAS]->(comment:Comment)
    RETURN post.id AS postid, comment
    ORDER BY comment.creation_time
    """
    try:
        comments = getGraphConnectionURI().cypher.execute(query)
        return comments
    except cypher.CypherError, cypher.CypherTransactionError:
        raise "Exception occured in function get_all_recent_comments "


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
# function : convertMilliSecondsToNormalDate
# purpose : function to convert milliseconds to normal date time
# params : milliseconds
# returns : returns date
# Exceptions : None
############################################################################

def convertMilliSecondsToNormalDate(milliseconds):
    seconds = milliseconds / 1000.0
    normalDateTime = datetime.datetime.fromtimestamp(seconds).strftime('%Y-%m-%d %H:%M:%S.%f')
    return normalDateTime


############################################################################
# function : date
# purpose : function to return current date with given format
# params : None
# returns : returns current date in YYYY-DD-MM format
# Exceptions : None
############################################################################

def date():
    return datetime.datetime.now().strftime('%Y-%m-%d')


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
        createPendingSubscribeRelationshipQuery = """
                MATCH (u:User), (s:System)
                WHERE u.google_id = {google_id} and s.system_uid={system_uid}
                CREATE UNIQUE (u)-[rel:SYS_PENDING_SUBSCRIBER]->(s)
                RETURN rel
        """
        try:
            relationship_status = getGraphConnectionURI().cypher.execute(createPendingSubscribeRelationshipQuery,
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
        createSubscribeRelationshipQuery = """
                MATCH (u:User), (s:System)
                WHERE u.google_id = {google_id} and s.system_uid={system_uid}
                CREATE UNIQUE (u)-[rel:SYS_SUBSCRIBER]->(s)
                RETURN rel
        """
        try:
            relationship_status = getGraphConnectionURI().cypher.execute(createSubscribeRelationshipQuery,
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
        createPendingParticipateRelationshipQuery = """
                MATCH (u:User), (s:System)
                WHERE u.google_id = {google_id} and s.system_uid={system_uid}
                CREATE UNIQUE (u)-[rel:SYS_PENDING_PARTICIPANT]->(s)
                RETURN rel
        """
        try:
            relationship_status = getGraphConnectionURI().cypher.execute(createPendingParticipateRelationshipQuery,
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
        query = """
            MATCH (user:User)-[:SYS_DUMMY]->(system:System)
            WHERE user.sql_id = {sql_id}
            RETURN system
        """
        try:
            recommended_systems = getGraphConnectionURI().cypher.execute(query, sql_id=sql_id)
            return recommended_systems
        except cypher.CypherError, cypher.CypherTransactionError:
            raise "Exception occured in function get_recommended_systems"

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
