from py2neo import authenticate,Graph, Node, Relationship
from datetime import datetime as dt
import uuid
from aqxWeb.sc import app
app.config.from_pyfile('settings.cfg')

#graph = Graph("http://aquaponics_sc:bwadsXAk63y6R0uBHN2g@aquaponicssc.sb02.stations.graphenedb.com:24789/db/data/")
graph = Graph(app.config['CONNECTIONSETTING']);

class User:

    def __init__(self,username):
        '''
        self.firstname = firstname
        self.lastname = lastname
        self.dateofbirth = dateofbirth
        self.organization = organization
        self.email = email '''
        self.username = username

    def find(self):
        user = graph.find_one("User", "username", self.username)
        return user

    def updateprofile(self, displayname, email, organization):
        query = """
        MATCH(x:User)
        WHERE x.sql_id = 1
        SET x.username = {newdisplayname}, x.email = {newemail}
        """

        return graph.cypher.execute(query, newdisplayname=displayname, newemail=email)


    def verify_password(self, password):
        user = self.find()
        if user:
            return True
        else:
            return False

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
        graph.create(rel)

    def get_recent_posts(self):
        query = """
        MATCH (user:User)-[:POSTED]->(post:Post)
        WHERE user.username = {username}
        RETURN post
        ORDER BY post.timestamp DESC LIMIT 5
        """

        return graph.cypher.execute(query, username=self.username)

def get_todays_recent_posts():
    query = """
    MATCH (user:User)-[:POSTED]->(post:Post)
    WHERE post.date = {today}
    RETURN user.username AS username, post
    ORDER BY post.timestamp DESC LIMIT 5
    """

    return graph.cypher.execute(query, today=date())


def timestamp():
    epoch = dt.utcfromtimestamp(0)
    now = dt.now()
    delta = now - epoch
    return delta.total_seconds()

def date():
    return dt.now().strftime('%Y-%m-%d')


