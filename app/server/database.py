import motor.motor_asyncio
from neo4j import GraphDatabase
from bson.objectid import ObjectId

# mongodb

MONGO_DETAILS = "mongodb://localhost:27017"
NEO4J_DETAILS = "neo4j://localhost:7474"



class MongoClient:
    def __init__(self,port: int):
        self.mongo_client = motor.motor_asyncio.AsyncIOMotorClient("mongodb://localhost:" + str(port))
        self.network_db = self.mongo_client['network']
        self.repos_collection = self.network_db.get_collection("repos")
        self.users_collection = self.network_db.get_collection("users")
        self.comments_collection = self.network_db.get_collection("comments")
    
    @staticmethod
    def _repo_helper(repo_data: dict):
        return {
            '_id': repo_data['github_repo_id'],
            'name': repo_data['name'],
            'full_name': repo_data['full_name'],
            'stars': repo_data['stargazers_count'],
            'languages': repo_data['languages'],
            'created_at': repo_data['created_at'],
            'updated_at': repo_data['updated_at'],
            'forks_count': repo_data['forks_count'],
            'html_url': repo_data['html_url'],
        }

    @staticmethod
    def _user_helper(user_data: dict):
        return {
            '_id': user_data['github_user_id'],
            'username': user_data['username'],
            'name': user_data['name'],
            'avatar_url': user_data['avatar_url'],
            'bio': user_data['bio'],
            'languages': user_data['languages'],
            'following': user_data['following'],
            'followers': user_data['followers'],
            'html_url': user_data['html_url'],
        }

    @staticmethod
    def _comment_helper(comment_data: dict):
        return {
            '_id': comment_data['_id'],
            'score': comment_data['score'],
            'comment': comment_data['comment']
        }
    
    async def insert_repo(self,repo_data: dict):
        repo = await self.repos_collection.insert_one(MongoClient._repo_helper(repo_data))
        new_repo = await self.repos_collection.find_one({"_id": repo.inserted_id})
        return new_repo
    
    async def insert_user(self,user_data: dict):
        user = await self.users_collection.insert_one(MongoClient._user_helper(user_data))
        new_user = await self.users_collection.find_one({"_id": user.inserted_id})
        return new_user
    
    async def insert_comment(self,comment_data: dict):
        comment = await self.comments_collection.insert_one(MongoClient._comment_helper(comment_data))
        new_comment = await self.comments_collection.find_one({"_id": comment.inserted_id})
        return new_comment

    async def get_repos(self, query_options: dict):
        //TODO: ver como se haria paginado
        repos = []
        async for repo in self.repos_collection.find(query_options):
            repos.append(repo)
        return repos

    async def get_repo(self, query_options: dict):
        repo = await self.repos_collection.find_one(query_options)
        return repo

    async def get_users(self, query_options: dict):
        users = await self.users_collection.find(query_options)
        return users

    async def get_user(self, query_options: dict):
        user = await self.users_collection.find_one(query_options)
        return user

    async def get_comments(self, query_options: dict):
        comments = await self.comments_collection.find(query_options)
        return comments


# neo4j

class Neo4jClient:

    def __init__(self, port: int, user: str, password: str):
        self.driver = GraphDatabase.driver("neo4j://localhost:" + str(port), auth=(user, password))

    def close(self):
        self.driver.close()
    
    @staticmethod
    def _create_and_return_relation(tx, o1_id, o1_label, o2_id, o2_label, relation_label):
        query = (
            "MERGE (o1:" + o1_label + " { id: $o1_id }) "
            "MERGE  (o2:" + o2_label + " { id: $o2_id }) "
            "CREATE (o1)-[:" + relation_label + "]->(o2) "
            "RETURN o1, o2"
        )
        result = tx.run(query, o1_label=o1_label, o1_id=o1_id, o2_label=o2_label, o2_id=o2_id, relation_label=relation_label)
        try:
            return [{"o1": record["o1"]["id"], "o2": record["o2"]["id"]}
                    for record in result]
        # Capture any errors along with the query and data for traceability
        except ServiceUnavailable as exception:
            logging.error("{query} raised an error: \n {exception}".format(
                query=query, exception=exception))
            raise
        
    def create_ownership(self, owner_id, repo_id):
        with self.driver.session() as session:
            # Write transactions allow the driver to handle retries and transient errors
            result = session.write_transaction(
                Neo4jClient._create_and_return_relation, owner_id, "Person", repo_id, "Repository", "OWNS")
            for record in result:
                print("Created ownership between: {o1}, {o2}".format(
                    o1=record['o1'], o2=record['o2']))

    def create_contribution(self, contributor_id, repo_id):
        with self.driver.session() as session:
            # Write transactions allow the driver to handle retries and transient errors
            result = session.write_transaction(
                Neo4jClient._create_and_return_relation, contributor_id, "Person", repo_id, "Repository", "CONTRIBUTES_IN")
            for record in result:
                print("Created contribution between: {o1}, {o2}".format(
                    o1=record['o1'], o2=record['o2']))

    def create_following(self, follower_id, person_id):
        with self.driver.session() as session:
            # Write transactions allow the driver to handle retries and transient errors
            result = session.write_transaction(
                Neo4jClient._create_and_return_relation, follower_id, "Person", person_id, "Person", "FOLLOWS")
            for record in result:
                print("Created following between: {o1}, {o2}".format(
                    o1=record['o1'], o2=record['o2']))

    def create_review(self, person_id, repo_id):
        with self.driver.session() as session:
            # Write transactions allow the driver to handle retries and transient errors
            result = session.write_transaction(
                Neo4jClient._create_and_return_relation, person_id, "Person", repo_id, "Repository", "REVIEWS")
            for record in result:
                print("Created review between: {o1}, {o2}".format(
                    o1=record['o1'], o2=record['o2']))
    
    

mongo_client = MongoClient(27017)
neo_client = Neo4jClient(7687,'admin', 'admin')



