from py2neo import Graph, Node, Relationship, cypher
from datetime import datetime as dt
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

    def updateprofile(self, displayname, gender, organization, user_type, dateofbirth):
        query = """
        MATCH(x:User)
        WHERE x.sql_id = {sql_id}
        SET x.displayName = {newdisplayname}, x.gender = {newGender}, x.organization = {newOrganization}, x.user_type={newUserType}, x.dob = {newDOB}
        """
        try:
            return getGraphConnectionURI().cypher.execute(query, sql_id = self.sql_id, newdisplayname = displayname, newGender = gender, newOrganization = organization, newUserType=user_type, newDOB = dateofbirth)
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
            id = str(uuid.uuid4()),
            text = text,
            link = link,
            privacy = privacy,
            creation_time = timestamp(),
            modified_time = timestamp(),
            date = date()
        )
        rel = Relationship(user, "POSTED", post)
        try:
            getGraphConnectionURI().create(rel)
        except cypher.CypherError, cypher.CypherTransactionError:
            raise "Exception occured in function add_post "

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
        #print(user)
        comment = Node(
            "Comment",
            id=str(uuid.uuid4()),
            content=newcomment,
            user_sql_id=self.sql_id,
            user_display_name = user['displayName'],
            creation_time=timestamp(),
            modified_time=timestamp())
        post = getGraphConnectionURI().find_one("Post", "id", postid)
        rel = Relationship(post, 'HAS', comment)
        try:
            getGraphConnectionURI().create(rel)
        except cypher.CypherError, cypher.CypherTransactionError:
            raise "Exception occured in function add_comment "

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
    # function : get_search_friends
    # purpose : gets all the friends that is present in the Neo4J database
    # params : None
    # returns : Nodes labeled User
    # Exceptions : cypher.CypherError, cypher.CypherTransactionError
    ############################################################################
    def get_search_friends(self):
        query = """
            MATCH (users:User)
            RETURN users.givenName, users.familyName, users.organization
        """

        try:
            results = getGraphConnectionURI().cypher.execute(query);
            return results;
        except cypher.CypherError, cypher.CypherTransactionError:
            raise "Exception occured in function get_search_friends"

    #END OF USER class

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
# purpose : gets current timestamp value
# params : None
# returns : timestamp in seconds
# Exceptions : None
############################################################################

def timestamp():
    epoch = dt.utcfromtimestamp(0)
    now = dt.now()
    delta = now - epoch
    return delta.total_seconds()

############################################################################
# function : date
# purpose : function to return current date with given format
# params : None
# returns : returns current date in YYYY-DD-MM format
# Exceptions : None
############################################################################

def date():
    return dt.now().strftime('%Y-%m-%d')




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
    # purpose : gets the system details for the matched system name
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
            regExPattern = '(?i).*' + systemName +'.*'
            system_details = getGraphConnectionURI().cypher.execute(query, systemName = regExPattern)
            return system_details
        except cypher.CypherError, cypher.CypherTransactionError:
                raise "Exception occured in function get_system_by_name"



    ############################################################################
    # function : get_admin_systems
    # purpose : gets the system details where the specified user is admin for those systems
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
            admin_systems = getGraphConnectionURI().cypher.execute(query, sql_id = sql_id)
            return admin_systems
        except cypher.CypherError, cypher.CypherTransactionError:
                raise "Exception occured in function get_admin_systems"



    ############################################################################
    # function : get_participated_systems
    # purpose : gets the system details where the user has participated for
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
            participated_systems = getGraphConnectionURI().cypher.execute(query, sql_id = sql_id)
            return participated_systems
        except cypher.CypherError, cypher.CypherTransactionError:
                raise "Exception occured in function get_participated_systems"


    ############################################################################
    # function : subscribed_systems
    # purpose : gets the system details where the user has subscribed for
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
            subscribed_systems = getGraphConnectionURI().cypher.execute(query, sql_id = sql_id)
            return subscribed_systems
        except cypher.CypherError, cypher.CypherTransactionError:
                raise "Exception occured in function get_subscribed_systems"



    ############################################################################
    # function : get_recommended_systems
    # purpose : gets the recommended system details for the specified user
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
            recommended_systems = getGraphConnectionURI().cypher.execute(query, sql_id = sql_id)
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

