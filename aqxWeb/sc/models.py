from py2neo import authenticate, Graph, Node, Relationship, cypher
from flask import request
from urlparse import urlparse
import time
import datetime
import uuid
import requests
import json
from flask import url_for


def graph_update(query, **kwargs):
    """py2neo has significant changes in the API between V2 and V3,
    this function tries to be compatible to both APIs"""
    global graph_instance
    try:
        return graph_instance.cypher.execute(query, kwargs)
    except Exception as e:
        cursor = graph_instance.run(query, kwargs)
        return [r for r in cursor]


def graph_query(query, **kwargs):
    global graph_instance
    try:
        return graph_instance.cypher.execute(query, kwargs)
    except:
        cursor = graph_instance.run(query, kwargs)
        return [r for r in cursor]

def graph_query_one_or_none(query, **kwargs):
    global graph_instance
    try:
        result = graph_instance.cypher.execute(query, kwargs)
        if result is not None:
            return result.one
    except:
        cursor = graph_instance.run(query, kwargs)
        result = [r for r in cursor]
        if len(result) > 0:
            if len(result[0]) == 1:
                return result[0][0]
            return result
    return None


def init_sc_app(app):
    try:
        global app_instance
        app_instance = app
        global graph_instance
        authenticate(get_app_instance().config['NEO4J_HOST'],
                     get_app_instance().config['NEO4J_USER'],
                     get_app_instance().config['NEO4J_PASS'])
        graph_instance = Graph(get_app_instance().config['NEO4J_CONNECTION_URI'])
    except Exception as ex:
        print "Exception At init_sc_app: " + str(ex.message)
        raise


def get_app_instance():
    return app_instance


def social_graph():
    return graph_instance


class User:
    """User class contains information related to the user who is logged in"""

    def __init__(self, sql_id):
        self.sql_id = sql_id

    def find(self):
        return social_graph().find_one("User", "sql_id", self.sql_id)

    def update_profile(self, given_name, family_name, display_name, gender, organization, user_type, dob):
        query = """
        MATCH(x:User)
        WHERE x.sql_id = {sql_id}
        SET x.givenName = {given_name}, x.familyName = {family_name},
         x.displayName = {display_name}, x.gender = {gender},
         x.organization = {organization},
         x.user_type={user_type}, x.dob = {dob}
        """
        return graph_update(query, sql_id=self.sql_id, given_name=given_name,
                            family_name=family_name, display_name=display_name,
                            gender=gender, organization=organization,
                            user_type=user_type, dob=dob)

    def redirect_url(default='social.index'):
        return request.args.get('next') or \
               request.referrer or \
               url_for(default)

    def verify_password(self, password):
        user = self.find()
        if user:
            return True
        else:
            return False

    def add_post(self, text, privacy, link, profile=None, title="", img="", description=""):
        user = self.find()
        post = Node(
            "Post",
            id=str(uuid.uuid4()),
            text=text,
            privacy=privacy,
            creation_time=timestamp(),
            modified_time=timestamp(),
            date=date(),
            link=link,
            link_title=title,
            link_img=img,
            link_description=description
        )
        rel_post = Relationship(user, "POSTED", post)

        social_graph().create(rel_post)

        # if it is published in someone else's profile page
        if profile:
            rel_posted_to = Relationship(post, "POSTED_TO", profile)
            social_graph().create(rel_posted_to)

    def add_post_to(self, user_id, posted_to_user_id):
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
        post_node = graph_query(query, sql_id=user_id)
        graph_update(command, sql_id=posted_to_user_id, post_id=post_node[0]['post_id'])

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
        social_graph().create(rel)

    def check_status(self, sessionID, user_sql_id):
        friend_status = "Add friend"
        sentreq_res, receivedreq_res, friends_res = User(sessionID).get_friends_and_sent_req()
        for sf in sentreq_res:
            sf_id = sf[0]
            if user_sql_id == sf_id:
                friend_status = "Sent Friend Request"
        for rf in receivedreq_res:
            rf_id = rf[0]
            if user_sql_id == rf_id:
                friend_status = "Received Friend Request"
        for fr in friends_res:
            fr_id = fr[0]
            if user_sql_id == fr_id:
                friend_status = "Friends"
        if user_sql_id == sessionID:
            friend_status = "Me"
        return friend_status

    def edit_post(self, new_content, post_id):
        query = """
        MATCH (post:Post)
        WHERE post.id = {post_id}
        SET post.text = {new_content},
        post.modified_time = {time_now}
        RETURN post
        """
        graph_update(query, post_id=post_id, new_content=new_content, time_now=timestamp())

    def get_user_sql_id(self):
        return self.sql_id

    def delete_post(self, post_id):
        """Note: dangerous - deletes without asking whether this user owns the post TODO"""
        post = social_graph().find_one("Post", "id", post_id)

        # Deletes comments and all related relationships
        deleteCommentsQuery = """
            MATCH (post:Post)-[r:HAS]->(comment:Comment)
            WHERE post.id= {postid}
            DETACH DELETE comment
            """
        graph_update(deleteCommentsQuery, postid=post_id)

        # Deletes posts and all related relationships
        deletePostQuery = """
            MATCH (post:Post)
            WHERE post.id= {postid}
            DETACH DELETE post
            """
        graph_update(deletePostQuery, postid=post_id)

    def add_comment(self, new_comment, post_id):
        user = self.find()
        comment = Node(
            "Comment",
            id=str(uuid.uuid4()),
            content=new_comment,
            user_sql_id=self.sql_id,
            user_display_name=user['displayName'],
            creation_time=timestamp(),
            modified_time=timestamp())

        post = social_graph().find_one("Post", "id", post_id)
        rel = Relationship(post, 'HAS', comment)
        social_graph().create(rel)

    def test_add_comment(self, new_comment, post_id):
        user = self.find()
        # print(user)
        comment = Node(
            "Comment",
            id=str(1),
            content=new_comment,
            user_sql_id=self.sql_id,
            user_display_name=user['displayName'],
            creation_time=timestamp(),
            modified_time=timestamp())
        post = social_graph().find_one("Post", "id", post_id)
        rel = Relationship(post, 'HAS', comment)
        social_graph().create(rel)

    def edit_comment(self, new_comment, comment_id):
        user = self.find()
        query = """
        MATCH (comment:Comment)
        WHERE comment.id = {comment_id}
        SET comment.content = {new_comment},
        comment.modified_time = {timenow}
        RETURN comment
        """
        graph_update(query, comment_id=comment_id, new_comment=new_comment, timenow=timestamp())

    def delete_comment(self, comment_id):
        user = self.find()
        # print("Comment id" + str(comment_id))
        query = """
        MATCH (comment:Comment)
        WHERE comment.id = {comment_id}
        DETACH DELETE comment
        """
        graph_update(query, comment_id=comment_id)

    def like_post(self, post_id):
        user = self.find()
        post = social_graph().find_one("Post", "id", post_id)
        rel = Relationship(user, 'LIKED', post)
        social_graph().create_unique(rel)

    def unlike_post(self, post_id):
        user_sql_id = self.sql_id
        query = """
            MATCH (u:User)-[r:LIKED]->(p:Post)
            WHERE p.id= {postid} and u.sql_id = {user_sql_id}
            DELETE r
        """
        graph_update(query, postid=post_id, user_sql_id=user_sql_id)

    def get_search_friends(self):
        query = """
            MATCH (users:User)
            RETURN users.givenName, users.familyName, users.organization,
                   users.sql_id, users.email, users.google_id
        """
        return graph_query(query)

    def get_friends_and_sent_req(self):
        my_sql_id = self.sql_id
        my_sent_req_query = "MATCH (sentrequests { sql_id:{sql_id} })-[:SentRequest]->(res) RETURN res.sql_id"
        my_received_query = "MATCH (receivedrequests { sql_id:{sql_id} })<-[:SentRequest]-(res) RETURN res.sql_id"
        my_friends_query = "MATCH (friends { sql_id:{sql_id} })-[:FRIENDS]-(res) RETURN res.sql_id"

        sentreq_res = graph_query(my_sent_req_query, sql_id=my_sql_id)
        receivedreq_res = graph_query(my_received_query, sql_id=my_sql_id)
        frnds_res = graph_query(my_friends_query, sql_id=my_sql_id)
        return sentreq_res, receivedreq_res, frnds_res

    def send_friend_request(self, receiver_sql_id):
        my_user_node = self.find()
        friend_user_node = User(int(receiver_sql_id)).find()

        query = """
            MATCH  (n:User),(n1:User)
            Where n.sql_id = {sender_sid} AND n1.sql_id = {receiver_sid}
            CREATE (n)- [r:SentRequest] ->(n1)
            RETURN r
        """
        graph_update(query, sender_sid=my_user_node.properties["sql_id"],
                     receiver_sid=friend_user_node.properties["sql_id"])

    def accept_friend_request(self, sender_sql_id):
        my_user_node = self.find()
        friend_user_node = User(int(sender_sql_id)).find()
        # print(date());
        # print("In accept_friend_request")
        query = """
            MATCH (n:User),(n1:User)
            Where n.sql_id = {acceptor_sid} AND n1.sql_id = {accepted_sid}
            CREATE (n)- [r:FRIENDS{date:{today},blocker_id:{blocker_id}}] ->(n1)
        """
        graph_update(query, acceptor_sid=my_user_node.properties["sql_id"],
                     accepted_sid=friend_user_node.properties["sql_id"],
                     today=date(), blocker_id='')

    def block_a_friend(self, blocked_sql_id):
        my_user_node = self.find()
        blocked_user_node = User(int(blocked_sql_id)).find()
        query = """
            match (n1:User)-[r:FRIENDS]-(n2:User)
            where n1.sql_id = {blocker_sid} and n2.sql_id = {blocked_sid}
            set r.blocker_id={blocker_id}
            return r
        """
        graph_update(query, blocker_sid=my_user_node.properties["sql_id"],
                     blocked_sid=blocked_user_node.properties["sql_id"],
                     blocker_id=str((my_user_node.properties["sql_id"])))

    def unblock_a_friend(self, blocked_sql_id):
        my_user_node = self.find()
        blocked_user_node = User(int(blocked_sql_id)).find()
        query = """
            match (n1:User)-[r:FRIENDS]-(n2:User)
            where n1.sql_id = {blocker_sid} and n2.sql_id = {blocked_sid}
            set r.blocker_id={blocker_id};
        """
        graph_update(query, blocker_sid=my_user_node.properties["sql_id"],
                     blocked_sid=blocked_user_node.properties["sql_id"],
                     today=date(), blocker_id='')

    def delete_friend_request(self, receiver_sql_id):
        my_user_node = self.find()
        receiver_user_node = User(int(receiver_sql_id)).find()
        # print("In delete_friend_request")
        query = """
            MATCH  (n:User) - [r:SentRequest] - (n1:User)
            Where n.sql_id = {acceptor_sid} AND n1.sql_id = {accepted_sid}
            delete r
        """
        graph_update(query, acceptor_sid=my_user_node.properties["sql_id"],
                     accepted_sid=receiver_user_node.properties["sql_id"])


    def delete_friend(self, receiver_sql_id):
        my_user_node = self.find()
        receiver_user_node = User(int(receiver_sql_id)).find()
        query = """
            MATCH  (n:User) - [r:FRIENDS] - (n1:User)
            Where n.sql_id = {acceptor_sid} AND n1.sql_id = {accepted_sid}
            delete r

        """
        graph_update(query, acceptor_sid=my_user_node.properties["sql_id"],
                     accepted_sid=receiver_user_node.properties["sql_id"])

    def get_pending_friend_request(self, u_sql_id):
        query = """
            MATCH (n:User)-[r:SentRequest]->(n1:User)
            WHERE n1.sql_id = {u_sql_id}
            return n
            ORDER BY n.givenName
        """
        return graph_query(query, u_sql_id=u_sql_id)

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
        return graph_query(reco_friends_query, sql_id=my_sql_id)

    def get_mutual_friends(self, other_sid):
        my_sql_id = self.sql_id
        mutual_query = """
        MATCH (me { sql_id: {my_sid} }),(other)
            WHERE other.sql_id = {oth_sid}
            OPTIONAL MATCH pMutualFriends=(me)-[:FRIENDS]-(mf)-[:FRIENDS]-(other)
            RETURN mf.sql_id AS mf_sid, mf.givenName+" "+mf.familyName AS mf_name, mf.google_id AS mf_gid
            """
        return graph_query(mutual_query, my_sid=my_sql_id, oth_sid=other_sid)

    def get_my_friends(self, u_sql_id):
        my_sql_id = u_sql_id
        query = """
            MATCH (n:User)-[r:FRIENDS]-(n1:User)
            WHERE n1.sql_id = {sql_id} and r.blocker_id = {blocker_id}
            return n
            ORDER BY n.givenName
        """
        return graph_query(query, sql_id=my_sql_id, blocker_id="")

    def is_friend(self, u_sql_id1, u_sql_id2):
        query = """
        MATCH (n:User)-[r:FRIENDS]-(f:User)
        WHERE n.sql_id = {sql_id1} and f.sql_id = {sql_id2} and r.blocker_id = {blocker_id}
        return r
        """
        return graph_query(query, sql_id1=u_sql_id1, sql_id2=u_sql_id2, blocker_id="")

    def get_my_blocked_friends(self, u_sql_id):
        my_sql_id = u_sql_id
        query = """
            MATCH (n:User)-[r:FRIENDS]-(n1:User)
            WHERE n1.sql_id = {sql_id}  and r.blocker_id = {blocker_id}
            return n
            ORDER BY n.givenName
        """
        return graph_query(query, sql_id=my_sql_id, blocker_id=str(my_sql_id))

    def get_user_by_google_id(self, google_id):
        query = """
            MATCH (user:User)
            WHERE user.google_id = {google_id}
            RETURN user
        """
        return graph_query_one_or_none(query, google_id=google_id)


########### END OF USER class #############


def get_system_measurements_dav_api(system_uid):
    """
    purpose : gets measurements for the system from dav team db for given system uid
    params :
        system_uid - id which uniqly represents the system
    returns : json string of system_uid and measurements array"""
    try:
        base_url = urlparse(request.url).netloc
        dav_system_measurement_url = "http://" + str(base_url) + "/dav/aqxapi/v1/measurements"
        app = get_app_instance()
        with app.test_client() as client:
            query_param = {'system_uid': system_uid}
            response = client.get(dav_system_measurement_url, query_string=query_param)
            return response.data
    except Exception as ex:
        print "Exception in get_system_measurements_dav_api"
        print str(ex)


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
    return graph_query(query, sql_id=user_id)


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
    return graph_query(query, sql_id=user_id)


def get_all_recent_comments():
    query = """
    MATCH (user:User),(post:Post)-[:HAS]->(comment:Comment)
    WHERE user.sql_id = comment.user_sql_id
    RETURN post.id AS postid, user, comment
    ORDER BY comment.creation_time
    """
    return graph_query(query)


def get_total_likes_for_posts():
    query = """
    MATCH (u:User)-[r:LIKED]->(p:Post)
    RETURN p.id as postid, count(*) as likecount
    """
    return graph_query(query)


def get_all_post_owners():
    query = """
    MATCH (u:User)-[r:POSTED]->(p:Post)
    RETURN p.id as postid, u.sql_id as userid
    ORDER BY p.modified_time DESC
    """
    return graph_query(query)


def get_all_recent_likes():
    query = """
    MATCH (u:User)-[r:LIKED]->(p:Post)
    RETURN p.id as postid, u.sql_id as userid
    ORDER BY p.modified_time DESC
    """
    return graph_query(query)


def timestamp():
    return int(round(time.time() * 1000))


def convert_milliseconds_to_normal_date(milliseconds):
    seconds = milliseconds / 1000.0
    return datetime.datetime.fromtimestamp(seconds).strftime('%m-%d-%Y %H:%M')


def date():
    return datetime.datetime.now().strftime('%Y-%m-%d')


def get_sql_id(google_id):
    query = """
        MATCH (user:User)
        WHERE user.google_id = {google_id}
        RETURN user.sql_id as sql_id
    """
    return graph_query_one_or_none(query, google_id=google_id)


def get_address_from_lat_lng(latitude, longitude):
    address = ""
    try:
        geocode_api_base_url = "https://maps.googleapis.com/maps/api/geocode/json?address="
        geocode_api_url = geocode_api_base_url + str(latitude) + "," + str(longitude)
        google_api_response = requests.get(geocode_api_url)
        # For successful API call, response code will be 200 (OK)
        if (google_api_response.ok):
            jData = json.loads(google_api_response.content)
            if (len(jData['results']) > 0):
                address = jData['results'][0]['formatted_address']
        return address
    except Exception as e:
        return address


def update_profile_image_url(sql_id, image_url):
    update_image_url_query = """
        MATCH (u:User)
        WHERE u.sql_id = {sql_id}
        SET u.image_url = {image_url}
        RETURN u
    """
    graph_update(update_image_url_query, sql_id=sql_id, image_url=image_url)



class System:
    """Contains information related to the system"""

    def __init__(self):
        self.system_uid = None

    def find(self, system_uid):
            return social_graph().find_one("System", "system_uid", system_uid)

    def get_system_post_owners(self, system_uid):
        query = """
        MATCH (u:User)-[r:USER_POSTED]->(p:SystemPost)<-[r2:SYS_POSTED]-(s:System)
        WHERE s.system_uid = {system_uid}
        RETURN p.id as postid, u.sql_id as userid
        ORDER BY p.modified_time DESC
        """
        return graph_query(query, system_uid=system_uid)

    def get_system_recent_likes(self, system_uid):
        query = """

        MATCH (u:User)-[r:SYS_LIKED]->(p:SystemPost)<-[r1:SYS_POSTED]-(s:System)
        WHERE s.system_uid = {system_uid}
        RETURN p.id as postid, u.sql_id as userid
        ORDER BY p.modified_time DESC
        """
        return graph_query(query, system_uid=system_uid)

    def get_total_likes_for_system_posts(self, system_uid):
        query = """
        MATCH (u:User)-[r:SYS_LIKED]->(p:SystemPost)<-[r1:SYS_POSTED]-(s:System)
        WHERE s.system_uid = {system_uid}
        RETURN p.id as postid, count(*) as likecount
        """
        return graph_query(query, system_uid=system_uid)

    def get_system_recent_posts(self, system_uid):
        query = """
        MATCH (system:System)-[r1:SYS_POSTED]->(post:SystemPost)<-[r2:USER_POSTED]-(user:User)
        WHERE system.system_uid = {system_uid}
        RETURN user.displayName AS displayName, user, post
        ORDER BY post.modified_time DESC
        """
        return graph_query(query, system_uid=system_uid)

    def get_system_recent_comments(self, system_uid):
        query = """
        MATCH (user:User),
        (system:System)-[r1:SYS_POSTED]->(post:SystemPost)-[r:HAS]->(comment:SystemComment)
        WHERE system.system_uid = {system_uid}
            and user.sql_id = comment.user_sql_id
        RETURN post.id AS postid, user, comment
        ORDER BY comment.creation_time
        """
        return graph_query(query, system_uid=system_uid)

    def get_system_by_name(self, system_name):
        query = """
            MATCH (system:System)
            WHERE system.name =~ {system_name}
            RETURN system
        """
        regex_pattern = '(?i).*' + system_name + '.*'
        return graph_query(query, system_name=regex_pattern)

    def get_system_by_uid(self, system_uid):
        query = """
            MATCH (system:System)
            WHERE system.system_uid = {system_uid}
            RETURN system
        """
        return graph_query(query, system_uid=system_uid)

    def get_admin_systems(self, sql_id):
        query = """
            MATCH (user:User)-[:SYS_ADMIN]->(system:System)
            WHERE user.sql_id = {sql_id}
            RETURN system
            ORDER BY system.name
        """
        return graph_query(query, sql_id=sql_id)

    def get_system_admins(self, system_uid):
        query = """
            MATCH (user:User)-[rel:SYS_ADMIN]->(sys:System)
            WHERE sys.system_uid = {system_uid}
            return user, count(*) as total_admins
            ORDER BY user.givenName
        """
        return graph_query(query, system_uid=system_uid)

    def get_participated_systems(self, sql_id):
        query = """
            MATCH (user:User)-[:SYS_PARTICIPANT]->(system:System)
            WHERE user.sql_id = {sql_id}
            RETURN system
            ORDER BY system.name
        """
        return graph_query(query, sql_id=sql_id)

    def get_user_privilege_for_system(self, sql_id, system_uid):
        user_privilege = None
        query = """
             match (user:User)-[r]->(system:System)
             WHERE user.sql_id = {sql_id} and system.system_uid = {system_uid}
             return type(r) as rel_type
        """
        relationship_type = graph_query(query, sql_id=sql_id, system_uid=system_uid)
        if not relationship_type or len(relationship_type) == 0:
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

    def approve_system_participant(self, google_id, system_uid):
        remove_relationship_query = """
                MATCH (u:User)-[rel:SYS_PENDING_PARTICIPANT]->(s:System)
                WHERE u.google_id = {google_id} and s.system_uid={system_uid}
                DETACH DELETE rel
        """
        create_relationship_query = """
                MATCH (u:User), (s:System)
                WHERE u.google_id = {google_id} and s.system_uid={system_uid}
                CREATE UNIQUE (u)-[rel:SYS_PARTICIPANT]->(s)
                RETURN rel
        """
        graph_update(remove_relationship_query, google_id=google_id, system_uid=system_uid)
        graph_update(create_relationship_query, google_id=google_id, system_uid=system_uid)


    def reject_system_participant(self, google_id, system_uid):
        remove_relationship_query = """
                MATCH (u:User)-[rel:SYS_PENDING_PARTICIPANT]->(s:System)
                WHERE u.google_id = {google_id} and s.system_uid={system_uid}
                DETACH DELETE rel
        """
        graph_update(remove_relationship_query, google_id=google_id, system_uid=system_uid)


    def pending_subscribe_to_system(self, google_id, system_uid):
        remove_relationship_query = """
                MATCH (u:User)-[rel]->(s:System)
                WHERE u.google_id = {google_id} and s.system_uid={system_uid}
                DETACH DELETE rel
        """
        create_pending_subscriber_rel_query = """
                MATCH (u:User), (s:System)
                WHERE u.google_id = {google_id} and s.system_uid={system_uid}
                CREATE UNIQUE (u)-[rel:SYS_PENDING_SUBSCRIBER]->(s)
                RETURN rel
        """
        graph_update(remove_relationship_query, google_id=google_id, system_uid=system_uid)
        graph_update(create_pending_subscriber_rel_query, google_id=google_id, system_uid=system_uid)

    def subscribe_to_system(self, google_id, system_uid):
        remove_relationship_query = """
                MATCH (u:User)-[rel]->(s:System)
                WHERE u.google_id = {google_id} and s.system_uid={system_uid}
                DETACH DELETE rel
        """
        create_subscriber_relationship_query = """
                MATCH (u:User), (s:System)
                WHERE u.google_id = {google_id} and s.system_uid={system_uid}
                CREATE UNIQUE (u)-[rel:SYS_SUBSCRIBER]->(s)
                RETURN rel
        """
        graph_update(remove_relationship_query, google_id=google_id, system_uid=system_uid)
        graph_update(create_subscriber_relationship_query, google_id=google_id, system_uid=system_uid)

    def pending_participate_to_system(self, google_id, system_uid):
        remove_relationship_query = """
                MATCH (u:User)-[rel]->(s:System)
                WHERE u.google_id = {google_id} and s.system_uid={system_uid}
                DETACH DELETE rel
        """
        create_pending_participate_relationship_query = """
                MATCH (u:User), (s:System)
                WHERE u.google_id = {google_id} and s.system_uid={system_uid}
                CREATE UNIQUE (u)-[rel:SYS_PENDING_PARTICIPANT]->(s)
                RETURN rel
        """
        graph_update(remove_relationship_query, google_id=google_id, system_uid=system_uid)
        graph_update(create_pending_participate_relationship_query, google_id=google_id, system_uid=system_uid)

    def leave_system(self, google_id, system_uid):
        remove_relationship_query = """
                MATCH (u:User)-[rel]->(s:System)
                WHERE u.google_id = {google_id} and s.system_uid={system_uid}
                DETACH DELETE rel
        """
        graph_update(remove_relationship_query, google_id=google_id, system_uid=system_uid)

    def delete_system_participant(self, google_id, system_uid):
        remove_relationship_query = """
                MATCH (u:User)-[rel:SYS_PARTICIPANT]->(s:System)
                WHERE u.google_id = {google_id} and s.system_uid={system_uid}
                DETACH DELETE rel
        """
        graph_update(remove_relationship_query, google_id=google_id, system_uid=system_uid)

    def make_admin_for_system(self, google_id, system_uid):
        remove_relationship_query = """
                MATCH (u:User)-[rel]->(s:System)
                WHERE u.google_id = {google_id} and s.system_uid={system_uid}
                DETACH DELETE rel
        """
        create_admin_relationship_query = """
                MATCH (u:User), (s:System)
                WHERE u.google_id = {google_id} and s.system_uid={system_uid}
                CREATE UNIQUE (u)-[rel:SYS_ADMIN]->(s)
                RETURN rel
        """
        graph_update(remove_relationship_query, google_id=google_id, system_uid=system_uid)
        graph_update(create_admin_relationship_query, google_id=google_id, system_uid=system_uid)

    def make_participant_for_system(self, google_id, system_uid):
        remove_relationship_query = """
                MATCH (u:User)-[rel]->(s:System)
                WHERE u.google_id = {google_id} and s.system_uid={system_uid}
                DETACH DELETE rel
        """
        create_participant_relationship_query = """
                MATCH (u:User), (s:System)
                WHERE u.google_id = {google_id} and s.system_uid={system_uid}
                CREATE UNIQUE (u)-[rel:SYS_PARTICIPANT]->(s)
                RETURN rel
        """
        graph_update(remove_relationship_query, google_id=google_id, system_uid=system_uid)
        graph_update(create_participant_relationship_query, google_id=google_id, system_uid=system_uid)

    def make_subscriber_for_system(self, google_id, system_uid):
        remove_relationship_query = """
                MATCH (u:User)-[rel]->(s:System)
                WHERE u.google_id = {google_id} and s.system_uid={system_uid}
                DETACH DELETE rel
        """
        create_subscriber_relationship_query = """
                MATCH (u:User), (s:System)
                WHERE u.google_id = {google_id} and s.system_uid={system_uid}
                CREATE UNIQUE (u)-[rel:SYS_SUBSCRIBER]->(s)
                RETURN rel
        """
        graph_update(remove_relationship_query, google_id=google_id, system_uid=system_uid)
        graph_update(create_subscriber_relationship_query, google_id=google_id, system_uid=system_uid)

    def delete_system_admin(self, google_id, system_uid):
        remove_relationship_query = """
                MATCH (u:User)-[rel:SYS_ADMIN]->(s:System)
                WHERE u.google_id = {google_id} and s.system_uid={system_uid}
                DETACH DELETE rel
        """
        graph_update(remove_relationship_query, google_id=google_id, system_uid=system_uid)

    def delete_system_subscriber(self, google_id, system_uid):
        remove_relationship_query = """
                MATCH (u:User)-[rel:SYS_SUBSCRIBER]->(s:System)
                WHERE u.google_id = {google_id} and s.system_uid={system_uid}
                DETACH DELETE rel
        """
        graph_update(remove_relationship_query, google_id=google_id, system_uid=system_uid)

    def get_system_participants(self, system_uid):
        query = """
            MATCH (user:User)-[rel:SYS_PARTICIPANT]->(sys:System)
            WHERE sys.system_uid = {system_uid}
            return user as participants
            ORDER BY user.givenName
        """
        return graph_query(query, system_uid=system_uid)

    def get_participants_pending_approval(self, system_uid):
        query = """
            MATCH (user:User)-[rel:SYS_PENDING_PARTICIPANT]->(sys:System)
            WHERE sys.system_uid = {system_uid}
            return user as pending_participants
            ORDER BY user.givenName
        """
        return graph_query(query, system_uid=system_uid)

    def get_subscribed_systems(self, sql_id):
        query = """
            MATCH (user:User)-[:SYS_SUBSCRIBER]->(system:System)
            WHERE user.sql_id = {sql_id}
            RETURN system
            ORDER BY system.name
        """
        return graph_query(query, sql_id=sql_id)

    def get_system_subscribers(self, system_uid):
        query = """
            MATCH (user:User)-[rel:SYS_SUBSCRIBER]->(sys:System)
            WHERE sys.system_uid = {system_uid}
            return user as subscriber
            ORDER BY user.givenName
        """
        return graph_query(query, system_uid=system_uid)

    def get_subscribers_pending_approval(self, system_uid):
        query = """
            MATCH (user:User)-[rel:SYS_PENDING_SUBSCRIBER]->(sys:System)
            WHERE sys.system_uid = {system_uid}
            return user as pending_subscribers
            ORDER BY user.givenName
        """
        return graph_query(query, system_uid=system_uid)

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
        # Minimum Depth Level To Identify The Recommended Systems
        minimum_depth_level = 2
        friends_system = graph_query(friends_system_query, sql_id=sql_id)
        return System().get_mutual_system_between_friends(friends_system, minimum_depth_level)

    def add_system_post(self, system_uid, user_sql_id, text, privacy, link, title="", img="", description=""):
        new_system = System().find(system_uid)
        user = User(user_sql_id).find()
        post = Node(
            "SystemPost",
            id=str(uuid.uuid4()),
            text=text,
            privacy=privacy,
            userid=user_sql_id,
            creation_time=timestamp(),
            modified_time=timestamp(),
            date=date(),
            link=link,
            link_title=title,
            link_img=img,
            link_description=description
        )
        sys_post_relationship = Relationship(new_system, "SYS_POSTED", post)
        user_post_relationship = Relationship(user, "USER_POSTED", post)
        social_graph().create(sys_post_relationship)
        social_graph().create(user_post_relationship)

    def delete_system_comment(self, commentid):
        query = """
        MATCH (comment:SystemComment)
        WHERE comment.id = {commentid}
        DETACH DELETE comment
        """
        graph_update(query, commentid=commentid)

    def edit_system_comment(self, new_comment, comment_id):
        query = """
        MATCH (comment:SystemComment)
        WHERE comment.id = {commentid}
        SET comment.content = {newcomment},
        comment.modified_time = {timenow}
        RETURN comment
        """
        graph_update(query, commentid=comment_id, newcomment=new_comment, timenow=timestamp())

    def edit_system_post(self, new_content, post_id):
        query = """
        MATCH (post:SystemPost)
        WHERE post.id = {postid}
        SET post.text = {newcontent},
        post.modified_time = {timenow}
        RETURN post
        """
        graph_update(query, postid=post_id, newcontent=new_content, timenow=timestamp())

    def delete_system_post(self, post_id):
        # Deletes comments and all related relationships
        deleteSystemCommentsQuery = """
            MATCH (post:SystemPost)-[r:HAS]->(comment:SystemComment)
            WHERE post.id= {postid}
            DETACH DELETE comment
            """
        graph_update(deleteSystemCommentsQuery, postid=post_id)

        # Deletes posts and all related relationships
        deleteSystemPostQuery = """
            MATCH (post:SystemPost)
            WHERE post.id= {postid}
            DETACH DELETE post
            """
        graph_update(deleteSystemPostQuery, postid=post_id)

    def like_system_post(self, user_sql_id, system_postid):
        user = User(user_sql_id).find()
        post = social_graph().find_one("SystemPost", "id", system_postid)
        rel = Relationship(user, 'SYS_LIKED', post)
        social_graph().create_unique(rel)

    def add_system_comment(self, user_sql_id, new_comment, system_postid):
        user = User(user_sql_id).find()
        post = social_graph().find_one("SystemPost", "id", system_postid)
        comment = Node(
            "SystemComment",
            id=str(uuid.uuid4()),
            content=new_comment,
            user_sql_id=user_sql_id,
            user_display_name=user['displayName'],
            creation_time=timestamp(),
            modified_time=timestamp())
        rel = Relationship(post, 'HAS', comment)
        social_graph().create(rel)

    def unlike_system_post(self, user_sql_id, system_postid):
        user = User(user_sql_id).find()
        post = social_graph().find_one("SystemPost", "id", system_postid)
        query = """
            MATCH (u:User)-[r:SYS_LIKED]->(p:SystemPost)
            WHERE p.id= {postid} and u.sql_id = {userSqlId}
            DELETE r
        """
        graph_update(query, postid=system_postid, userSqlId=user_sql_id)

    def get_mutual_system_between_friends(self, friends_system, minimum_depth_level):
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
        return graph_query(system_query, system_uid_collection=list_of_mutual_systems.keys())

    def get_all_systems(self):
        query = """
            MATCH (system:System)
            RETURN system
            ORDER BY system.name
        """
        return graph_query(query)


class Privacy:
    """Contains the privacy information, such as default privacy and privacy options
    Defining Privacy enumeration in a simple way to avoiding extra dependencies"""

    # Constants Definition
    # Privacy Options
    FRIENDS = "Friends"
    PRIVATE = "Private"
    PUBLIC = "Public"
    PARTICIPANTS = "Participants"  # Participants Only

    def __init__(self, privacy_options, default_privacy, page_type, page_id):
        self.privacy_options = privacy_options
        self.default_privacy = default_privacy
        self.page_type = page_type
        self.page_id = page_id
        self.user_relation = Privacy.PUBLIC


class Group:

    def __init__(self):
        self.group_uid = None

    def get_groups(self):
        query = """
            MATCH (g:Group) RETURN g.name, g.description, g.group_uid """
        return graph_query(query)

    def create_group(self, user_sql_id, group_name, group_description, is_private):
        group_uid = str(uuid.uuid4())
        user = User(user_sql_id).find()
        group = Node(
            "Group",
            group_uid=group_uid,
            name=group_name,
            description=group_description,
            is_private_group=is_private,
            creation_time=timestamp(),
            modified_time=timestamp(),
            status=0,

        )
        user_groupadmin_relationship = Relationship(user, "GROUP_ADMIN", group)
        social_graph().create(group)
        social_graph().create(user_groupadmin_relationship)
        return group_uid

    def find(self, group_uid):
        return social_graph().find_one("Group", "group_uid", group_uid)

    def get_group_by_uid(self, group_uid):
        query = """
            MATCH (group:Group)
            WHERE group.group_uid = {group_uid}
            RETURN group
        """
        return graph_query(query, group_uid=group_uid)

    def add_group_post(self, group_uid, user_sql_id, text, privacy, link, title="", img="", description=""):
        group = Group().find(group_uid)
        user = User(user_sql_id).find()
        post = Node(
            "GroupPost",
            id=str(uuid.uuid4()),
            text=text,
            privacy=privacy,
            userid=user_sql_id,
            creation_time=timestamp(),
            modified_time=timestamp(),
            date=date(),
            link=link,
            link_title=title,
            link_img=img,
            link_description=description
        )
        group_post_relationship = Relationship(group, "GROUP_POSTED", post)
        user_group_post_relationship = Relationship(user, "USER_POSTED", post)
        social_graph().create(group_post_relationship)
        social_graph().create(user_group_post_relationship)

    def edit_group_post(self, new_content, post_id):
        query = """
        MATCH (post:GroupPost)
        WHERE post.id = {post_id}
        SET post.text = {new_content},
        post.modified_time = {time_now}
        RETURN post
        """
        graph_update(query, post_id=post_id, new_content=new_content, time_now=timestamp())

    def delete_group_post(self, post_id):
        # Deletes comments and all related relationships
        delete_group_comments_query = """
            MATCH (post:GroupPost)-[r:HAS]->(comment:GroupComment)
            WHERE post.id= {post_id}
            DETACH DELETE comment
            """
        graph_update(delete_group_comments_query, post_id=post_id)

        # Deletes posts and all related relationships
        delete_group_post_query = """
            MATCH (post:GroupPost)
            WHERE post.id= {post_id}
            DETACH DELETE post
            """
        graph_update(delete_group_post_query, post_id=post_id)

    def like_group_post(self, user_sql_id, group_postid):
        user = User(user_sql_id).find()
        post = social_graph().find_one("GroupPost", "id", group_postid)
        rel = Relationship(user, 'GROUP_LIKED', post)
        social_graph().create_unique(rel)

    def unlike_group_post(self, user_sql_id, group_postid):
        user = User(user_sql_id).find()
        post = social_graph().find_one("GroupPost", "id", group_postid)
        query = """
            MATCH (u:User)-[r:GROUP_LIKED]->(p:GroupPost)
            WHERE p.id= {postid} and u.sql_id = {userSqlId}
            DELETE r
        """
        graph_update(query, postid=group_postid, userSqlId=user_sql_id)

    def add_group_comment(self, user_sql_id, new_comment, group_postid):
        user = User(user_sql_id).find()
        post = social_graph().find_one("GroupPost", "id", group_postid)
        comment = Node(
            "GroupComment",
            id=str(uuid.uuid4()),
            content=new_comment,
            user_sql_id=user_sql_id,
            user_display_name=user['displayName'],
            creation_time=timestamp(),
            modified_time=timestamp())
        rel = Relationship(post, 'HAS', comment)
        social_graph().create(rel)

    def edit_group_comment(self, new_comment, comment_id):
        query = """
        MATCH (comment:GroupComment)
        WHERE comment.id = {commentid}
        SET comment.content = {newcomment},
        comment.modified_time = {timenow}
        RETURN comment
        """
        graph_update(query, commentid=comment_id, newcomment=new_comment, timenow=timestamp())

    def delete_group_comment(self, commentid):
        query = """
        MATCH (comment:GroupComment)
        WHERE comment.id = {commentid}
        DETACH DELETE comment
        """
        graph_update(query, commentid=commentid)

    def get_group_recent_comments(self, group_uid):
        query = """
        MATCH (user:User),
        (group:Group)-[r1:GROUP_POSTED]->(post:GroupPost)-[r:HAS]->(comment:GroupComment)
        WHERE group.group_uid = {group_uid}
            and user.sql_id = comment.user_sql_id
        RETURN post.id AS postid, user, comment
        ORDER BY comment.creation_time
        """
        return graph_query(query, group_uid=group_uid)

    def get_group_recent_posts(self, group_uid):
        query = """
        MATCH (group:Group)-[r1:GROUP_POSTED]->(post:GroupPost)<-[r2:USER_POSTED]-(user:User)
        WHERE group.group_uid = {group_uid}
        RETURN user.displayName AS displayName, user, post
        ORDER BY post.modified_time DESC
        """
        return graph_query(query, group_uid=group_uid)

    def get_group_recent_likes(self, group_id):
        query = """
        MATCH (u:User)-[r:GROUP_LIKED]->(p:GroupPost)<-[r1:GROUP_POSTED]-(g:Group)
        WHERE g.group_uid = {group_id}
        RETURN p.id as postid, u.sql_id as userid
        ORDER BY p.modified_time DESC
        """
        return graph_query(query, group_id=group_id)

    def get_total_likes_for_group_posts(self, group_uid):
        query = """
        MATCH (u:User)-[r:GROUP_LIKED]->(p:GroupPost)<-[r1:GROUP_POSTED]-(s:Group)
        WHERE s.group_uid = {group_uid}
        RETURN p.id as postid, count(*) as likecount
        """
        return graph_query(query, group_uid=group_uid)

    def get_group_post_owners(self, group_uid):
        query = """
        MATCH (u:User)-[r:USER_POSTED]->(p:GroupPost)<-[r2:GROUP_POSTED]-(s:Group)
        WHERE s.group_uid = {group_uid}
        RETURN p.id as postid, u.sql_id as userid
        ORDER BY p.modified_time DESC
        """
        return graph_query(query, group_uid=group_uid)

    def get_user_privilege_for_group(self, sql_id, group_uid):
        user_privilege = None
        query = """
             match (user:User)-[r]->(group:Group)
             WHERE user.sql_id = {sql_id} and group.group_uid = {group_uid}
             return type(r) as rel_type
        """
        relationship_type = graph_query(query, sql_id=sql_id, group_uid=group_uid)
        if not relationship_type or len(relationship_type) == 0:
            user_privilege = None
        else:
            rel_type = relationship_type[0]['rel_type']
            if (rel_type == "GROUP_ADMIN"):
                user_privilege = "GROUP_ADMIN"
            elif (rel_type == "GROUP_MEMBER"):
                user_privilege = "GROUP_MEMBER"
            elif (rel_type == "GROUP_PENDING_MEMBER"):
                user_privilege = "GROUP_PENDING_MEMBER"
        return user_privilege

    def get_group_admins(self, group_uid):
        query = """
            MATCH (user:User)-[rel:GROUP_ADMIN]->(group:Group)
            WHERE group.group_uid = {group_uid}
            return user
            ORDER BY user.givenName
        """
        return graph_query(query, group_uid=group_uid)

    def get_group_members(self, group_uid):
        query = """
            MATCH (user:User)-[rel:GROUP_MEMBER]->(group:Group)
            WHERE group.group_uid = {group_uid}
            return user
            ORDER BY user.givenName
        """
        return graph_query(query, group_uid=group_uid)

    def get_members_pending_approval(self, group_uid):
        query = """
            MATCH (user:User)-[rel:GROUP_PENDING_MEMBER]->(group:Group)
            WHERE group.group_uid = {group_uid}
            return user
            ORDER BY user.givenName
        """
        return graph_query(query, group_uid=group_uid)

    def approve_group_member(self, google_id, group_uid):
        remove_relationship_query = """
                MATCH (u:User)-[rel:GROUP_PENDING_MEMBER]->(g:Group)
                WHERE u.google_id = {google_id} and g.group_uid={group_uid}
                DETACH DELETE rel
        """
        create_relationship_query = """
                MATCH (u:User), (g:Group)
                WHERE u.google_id = {google_id} and g.group_uid={group_uid}
                CREATE UNIQUE (u)-[rel:GROUP_MEMBER]->(g)
                RETURN rel
        """
        graph_update(remove_relationship_query, google_id=google_id, group_uid=group_uid)
        graph_update(create_relationship_query, google_id=google_id, group_uid=group_uid)

    def reject_group_member(self, google_id, group_uid):
        remove_relationship_query = """
                MATCH (u:User)-[rel:GROUP_PENDING_MEMBER]->(g:Group)
                WHERE u.google_id = {google_id} and g.group_uid={group_uid}
                DETACH DELETE rel
        """
        graph_update(remove_relationship_query, google_id=google_id, group_uid=group_uid)

    def delete_group_admin(self, google_id, group_uid):
        remove_relationship_query = """
                MATCH (u:User)-[rel:GROUP_ADMIN]->(g:Group)
                WHERE u.google_id = {google_id} and g.group_uid={group_uid}
                DETACH DELETE rel
        """
        graph_update(remove_relationship_query, google_id=google_id, group_uid=group_uid)

    def make_admin_for_group(self, google_id, group_uid):
        remove_relationship_query = """
                MATCH (u:User)-[rel]->(g:Group)
                WHERE u.google_id = {google_id} and g.group_uid={group_uid}
                DETACH DELETE rel
        """
        create_admin_relationship_query = """
                MATCH (u:User), (g:Group)
                WHERE u.google_id = {google_id} and g.group_uid={group_uid}
                CREATE UNIQUE (u)-[rel:GROUP_ADMIN]->(g)
                RETURN rel
        """
        graph_update(remove_relationship_query, google_id=google_id, group_uid=group_uid)
        graph_update(create_admin_relationship_query, google_id=google_id, group_uid=group_uid)

    def delete_group_member(self, google_id, group_uid):
        remove_relationship_query = """
                MATCH (u:User)-[rel:GROUP_MEMBER]->(g:Group)
                WHERE u.google_id = {google_id} and g.group_uid={group_uid}
                DETACH DELETE rel
        """
        graph_update(remove_relationship_query, google_id=google_id, group_uid=group_uid)

    def leave_group(self, google_id, group_uid):
        remove_relationship_query = """
                MATCH (u:User)-[rel]->(g:Group)
                WHERE u.google_id = {google_id} and g.group_uid={group_uid}
                DETACH DELETE rel
        """
        graph_update(remove_relationship_query, google_id=google_id, group_uid=group_uid)

    def join_group_pending(self, google_id, group_uid):
        remove_relationship_query = """
                MATCH (u:User)-[rel]->(g:Group)
                WHERE u.google_id = {google_id} and g.group_uid={group_uid}
                DETACH DELETE rel
        """
        create_subscriber_relationship_query = """
                MATCH (u:User), (g:Group)
                WHERE u.google_id = {google_id} and g.group_uid={group_uid}
                CREATE UNIQUE (u)-[rel:GROUP_PENDING_MEMBER]->(g)
                RETURN rel
        """
        graph_update(remove_relationship_query, google_id=google_id, group_uid=group_uid)
        graph_update(create_subscriber_relationship_query, google_id=google_id, group_uid=group_uid)

    def join_group(self, google_id, group_uid):
        remove_relationship_query = """
                MATCH (u:User)-[rel]->(g:Group)
                WHERE u.google_id = {google_id} and g.group_uid={group_uid}
                DETACH DELETE rel
        """
        create_subscriber_relationship_query = """
                MATCH (u:User), (g:Group)
                WHERE u.google_id = {google_id} and g.group_uid={group_uid}
                CREATE UNIQUE (u)-[rel:GROUP_MEMBER]->(g)
                RETURN rel
        """
        graph_update(remove_relationship_query, google_id=google_id, group_uid=group_uid)
        graph_update(create_subscriber_relationship_query, google_id=google_id, group_uid=group_uid)

    def update_group_info(self, group_uid, name, description, is_private_group):
        update_query = """
                MATCH (g:Group)
                WHERE g.group_uid={group_uid}
                SET g.name = {name}, g.description = {description},
                g.is_private_group = {is_private_group},
                g.modified_time = {modified_time}
                RETURN g
        """
        graph_update(update_query, group_uid=group_uid, name=name, description=description,
                     is_private_group=is_private_group, modified_time=timestamp())

    def get_recommended_groups(self, sql_id):
        friends_group_query = """
            MATCH (friend:User)-[rel]->(group:Group),
            (mySelf:User)
            where mySelf.sql_id = {sql_id} and
            NOT (mySelf)-[:GROUP_MEMBER]-(group) and
            NOT (mySelf)-[:GROUP_ADMIN]-(group) and
            (mySelf)-[:FRIENDS]-(friend)
            return friend, group
            ORDER By friend.givenName
        """
        # Minimum Depth Level To Identify The Recommended Groups
        minimum_depth_level = 2
        friends_group = graph_query(friends_group_query, sql_id=sql_id)
        mutual_group_between_friends = Group().get_mutual_group_between_friends(friends_group,
                                                                                minimum_depth_level)
        return mutual_group_between_friends

    def get_mutual_group_between_friends(self, friends_group, minimum_depth_level):
        # Initial Dictionary to hold the mutual Groups between friend(s) For Processing
        list_of_mutual_groups_raw = {}
        # Dictionary to hold the mutual Groups between friend(s) - Depth Level 2
        list_of_mutual_groups = {}
        for each_friend_group in friends_group:
            friend = each_friend_group['friend']
            group = each_friend_group['group']
            group_uid = group['group_uid']
            # Do nothing when there exists no group_uid in the Group node of Neo4J Database
            if group_uid is not None:
                # If the key already exists, increment the occurrence by 1
                if list_of_mutual_groups_raw.has_key(group_uid):
                    group_occurrence = list_of_mutual_groups_raw[group_uid]
                    group_occurrence += 1
                    list_of_mutual_groups_raw[group_uid] = group_occurrence
                # If the key does not exists, set the occurrence to 1
                else:
                    system_occurrence = 1
                    list_of_mutual_groups_raw[group_uid] = system_occurrence
        # Add the system_uid to dictionary only when the depth level is met
        for group_uid in list_of_mutual_groups_raw.keys():
            group_occurrence = list_of_mutual_groups_raw[group_uid]
            if group_occurrence >= minimum_depth_level:
                list_of_mutual_groups[group_uid] = group_occurrence
        # Query to fetch the systems
        group_query = """
            MATCH (group:Group)
            where group.group_uid IN {group_uid_collection}
            return group
            ORDER By group.name
        """
        return graph_query(group_query, group_uid_collection=list_of_mutual_groups.keys())

    def get_group_members(self, group_uid):
        query = """
            MATCH (user:User)-[rel:GROUP_MEMBER]->(group:Group)
            WHERE group.group_uid = {group_uid}
            return user as Members
            ORDER BY user.givenName
        """
        return graph_query(query, group_uid=group_uid)

    def get_members_pending_approval(self, group_uid):
        query = """
            MATCH (user:User)-[rel:GROUP_PENDING_MEMBER]->(group:Group)
            WHERE group.group_uid = {group_uid}
            return user as PendingMembers
            ORDER BY user.givenName
        """
        return graph_query(query, group_uid=group_uid)

    def get_admin_groups(self, sql_id):
        query = """
            MATCH (user:User)-[:GROUP_ADMIN]->(group:Group)
            WHERE user.sql_id = {sql_id}
            RETURN group
            ORDER BY group.name
        """
        return graph_query(query, sql_id=sql_id)

    def get_member_groups(self, sql_id):
        query = """
            MATCH (user:User)-[:GROUP_MEMBER]->(group:Group)
            WHERE user.sql_id = {sql_id}
            RETURN group
            ORDER BY group.name
        """
        return graph_query(query, sql_id=sql_id)

    def get_users_to_invite_groups(self, group_uid):
        query_to_fetch_users = """
            MATCH (u:User), (g:Group)
            WHERE NOT (u)-[:GROUP_ADMIN]->(g)
            and NOT (u)-[:GROUP_MEMBER]->(g)
            and NOT (u)-[:GROUP_PENDING_MEMBER]->(g)
            and g.group_uid = {group_uid}
            RETURN u
            ORDER BY u.givenName
        """
        return graph_query(query_to_fetch_users, group_uid=group_uid)
