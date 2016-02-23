from py2neo import authenticate, Graph, Node, Relationship, cypher
from datetime import datetime as dt
import uuid
from aqxWeb.sc import app

# File for db configuration
app.config.from_pyfile('settings.cfg')

# Create / Load graph with the connection settings
graph = Graph(app.config['CONNECTIONSETTING'])

################################################################################
# Class : User
# Contains information related to the user who is logged in
################################################################################

class User:

    ############################################################################
    # function : __init__
    # purpose : main function sets username
    # params :
    #       username : username for user
    # returns : None
    # Exceptions : None
    ############################################################################

    def __init__(self,username):
        self.username = username

    ############################################################################
    # function : find
    # purpose : function used to find user name based on username
    # params : self (User)
    # returns : User node
    # Exceptions : cypher.CypherError, cypher.CypherTransactionError
    ############################################################################

    def find(self):
        try:
            user = graph.find_one("User", "username", self.username)
            return user
        except cypher.CypherError, cypher.CypherTransactionError:
            raise "Exception occured in function User.find()"

    ############################################################################
    # function : updateprofile
    # purpose : function used to update the user profile
    # params :
    #        displayname : display name which need to changed
    #        email : email for the user
    # returns : Boolean
    # Exceptions : None
    ############################################################################

    def updateprofile(self, displayname, dob):
        query = """
        MATCH(x:User)
        WHERE x.username = {username}
        SET x.name = {newdisplayname}, x.dob = {newDOB}
        """
        try:
            return graph.cypher.execute(query, username = self.username, newdisplayname = displayname, newDOB = dob)
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
            title= "Post",
            text=text,
            link=link,
            privacy=privacy,
            page_type="MyPage",
            timestamp=timestamp(),
            date=date()
        )
        rel = Relationship(user, "POSTED", post)
        try:
            graph.create(rel)
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
        comment = Node(
            "Comment",
            id=str(uuid.uuid4()),
            title= "Comment",
            content=newcomment,
            user=self.username,
            creation_time=timestamp(),
            modified_time=timestamp())
        post = graph.find_one("Post", "id", postid)
        rel = Relationship(post, 'HAS', comment)
        try:
            graph.create(rel)
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
        post = graph.find_one("Post", "id", postid)
        rel = Relationship(user, 'LIKED', post)
        try:
            graph.create_unique(rel)
        except cypher.CypherError, cypher.CypherTransactionError:
            raise "Exception occured in function like_post "

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
    RETURN user.username AS username, post
    ORDER BY post.timestamp DESC
    """
    try:
        posts = graph.cypher.execute(query)
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
        comments = graph.cypher.execute(query)
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
