import motor.motor_asyncio
from neo4j import GraphDatabase
import logging
from bson.objectid import ObjectId
from neo4j.exceptions import ServiceUnavailable
from fastapi.encoders import jsonable_encoder
import math
import json

with open("app/config.json") as file:
    config = json.load(file)
    server_url = config["server_url"]
    server_port = config["server_port"]

# mongodb
MONGO_DETAILS = "mongodb://localhost:27017"
NEO4J_DETAILS = "neo4j://localhost:7474"


class MongoClient:
    def __init__(self,port: int):
        #TODO: crear indice en fullname 
        self.mongo_client = motor.motor_asyncio.AsyncIOMotorClient("mongodb://localhost:" + str(port))
        self.network_db = self.mongo_client['network']
        self.repos_collection = self.network_db.get_collection("repos")
        self.users_collection = self.network_db.get_collection("users")
        self.reviews_collection = self.network_db.get_collection("reviews")
    
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
    def _review_helper(review_data: dict):
        # Autoassign _id
        return {
            'score': review_data['score'],
            'comment': review_data['comment'],
            'created_at': review_data['created_at']
        }
    
    async def insert_repo(self,repo_data: dict):
        repo = await self.repos_collection.insert_one(MongoClient._repo_helper(repo_data))
        new_repo = await self.repos_collection.find_one({"_id": repo.inserted_id})
        return new_repo
    
    async def insert_user(self,user_data: dict):
        user = await self.users_collection.insert_one(MongoClient._user_helper(user_data))
        new_user = await self.users_collection.find_one({"_id": user.inserted_id})
        return new_user
    
    async def insert_review(self,review_data: dict):
        review = await self.reviews_collection.insert_one(MongoClient._review_helper(review_data))
        print(review.inserted_id)
        new_review = await self.reviews_collection.find_one({"_id": review.inserted_id})
        new_review['_id'] = str(new_review['_id'])
        return new_review

    async def get_repos(self, order_by: str, asc: bool, page: int, limit: int):
        repos = []
        total = await self.repos_collection.count_documents({})
        total_pages = math.ceil(total/limit)
        asc_val = 1 if asc else -1
        async for repo in self.repos_collection.find(sort=[(order_by,asc_val)],skip=page*limit, limit=limit):
            print(repo)
            full_name = repo['full_name'].split('/')
            repo['reviews_url'] = f"http://{server_url}:{server_port}/repos/{full_name[0]}/{full_name[1]}/reviews"
            repos.append(repo)
        return repos,total_pages

    async def get_repo(self, username: str, reponame: str):
        full_name = username + '/' + reponame
        # repo = await self.repos_collection.find_one({'full_name': full_name})
        repo = await self.repos_collection.find_one({'full_name': {'$regex': '^{}$'.format(full_name),'$options': 'i'}})
        repo['reviews_url'] = f"http://{server_url}:{server_port}/repos/{full_name[0]}/{full_name[1]}/reviews"
        return repo

    async def get_users(self, query_options: dict):
        users = await self.users_collection.find(query_options)
        return users
    
    async def get_repos_recommendations_by_id(self, user: dict, repo_ids: list, page: int, limit: int):
        users = []
        print(f"repo ids: {repo_ids}")
        total = await self.repos_collection.count_documents({"_id": {"$in": repo_ids}})
        # aux = []
        # async for user in self.repos_collection.find({"_id": {"$in": repo_ids}}):
        #     aux.append(user)
        # print(len(aux))
        # print(len(repo_ids))
        total_pages = math.ceil(total/limit)
        # user_langs = user['languages']
        pipeline = [
            {"$match": 
                {"_id": {"$in": repo_ids}}
            },
            { "$project" : {
            "_id" : 1,
            "name":1,
            "full_name": 1,
            "stars": 1,
            "languages": 1,
            "created_at": 1,
            "updated_at": 1,
            "forks_count": 1,
            "html_url": 1,
            "score" : {
                "$sum" : [
                    # {"$multiply": 
                    #     [{"$size": "$stars"},0.7]
                    # },
                    {"$multiply": 
                        ["$stars",0.2]
                    },
                ]
            }
            } 
            }, 
            {"$sort" : {"score" : -1} },
            {"$skip": page*limit},
            {"$limit": limit}
        ]
        async for user in self.repos_collection.aggregate(pipeline):
            users.append(user)
        # async for user in self.users_collection.find({"_id": {"$in": user_ids}}):
        #     users.append(user)
        return users, total_pages

    async def get_user_recommendations_by_id(self, user: dict, user_ids: list, page: int, limit: int):
        users = []
        total = await self.users_collection.count_documents({"_id": {"$in": user_ids}})
        # aux = []
        # async for user in self.users_collection.find({"_id": {"$in": user_ids}}):
        #     aux.append(user)
        # print(len(aux))
        # print(len(user_ids))
        print(total)
        total_pages = math.ceil(total/limit)
        user_langs = user['languages']
        pipeline = [
            {"$match": 
                {"_id": {"$in": user_ids}}
            },
            { "$project" : {
            "_id" : 1,
            "username" : 1,
            "name" : 1,
            'avatar_url': 1,
            'bio': 1,
            'languages': 1,
            'following': 1,
            'followers': 1,
            'html_url': 1,
            "score" : {
                "$sum" : [
                    {"$multiply": 
                        [{"$size": "$languages"},0.7]
                    },
                    {"$multiply": 
                        ["$followers",0.2]
                    },
                ]
            }
            } 
            }, 
            {"$sort" : {"score" : -1} },
            {"$skip": page*limit},
            {"$limit": limit}
        ]
        async for user in self.users_collection.aggregate(pipeline):
            users.append(user)
        # async for user in self.users_collection.find({"_id": {"$in": user_ids}}):
        #     users.append(user)
        return users, total_pages

    async def get_user(self, username: str):
        user = await self.users_collection.find_one({'username': {'$regex': '^{}$'.format(username),'$options': 'i'}})
        return user

    async def get_reviews(self, review_ids, order_by: str, asc: bool, page: int, limit: int):
        reviews = []
        total = await self.reviews_collection.count_documents({})
        total_pages = math.ceil(total/limit)
        review_ids = [ObjectId(id) for id in review_ids]
        asc_val = 1 if asc else -1
        async for review in self.reviews_collection.find({"_id": {"$in": review_ids}},sort=[(order_by,asc_val)],skip=page*limit, limit=limit):
            review['_id'] = str(review['_id'])
            reviews.append(review)
        return reviews,total_pages


# neo4j

class Neo4jClient:

    def __init__(self, port: int, user: str, password: str):
        self.driver = GraphDatabase.driver("neo4j://localhost:" + str(port), auth=(user, password))

    def close(self):
        self.driver.close()
    
    @staticmethod
    def _create_and_return_relation_with_id(tx, o1_id, o1_label, o2_id, o2_label, relation_label, relation_id):
        query = (
            "MERGE (o1:" + o1_label + " { id: $o1_id }) "
            "MERGE  (o2:" + o2_label + " { id: $o2_id }) "
            "CREATE (o1)-[r:" + relation_label + " { id: $relation_id }]->(o2) "
            "RETURN o1, r, o2"
        )
        result = tx.run(query, o1_id=o1_id, o2_id=o2_id, relation_id=relation_id)
        try:
            return [{"o1": record["o1"]["id"], "r": record["r"]["id"], "o2": record["o2"]["id"]}
                    for record in result]
        # Capture any errors along with the query and data for traceability
        except ServiceUnavailable as exception:
            logging.error("{query} raised an error: \n {exception}".format(
                query=query, exception=exception))
            raise

    @staticmethod
    def _create_and_return_relation(tx, o1_id, o1_label, o2_id, o2_label, relation_label):
        query = (
            "MERGE (o1:" + o1_label + " { id: $o1_id }) "
            "MERGE  (o2:" + o2_label + " { id: $o2_id }) "
            "CREATE (o1)-[:" + relation_label + "]->(o2) "
            "RETURN o1, o2"
        )
        result = tx.run(query, o1_id=o1_id, o2_id=o2_id)
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
                self._create_and_return_relation, owner_id, "Person", repo_id, "Repository", "OWNS")
            for record in result:
                print("Created ownership between: {o1}, {o2}".format(
                    o1=record['o1'], o2=record['o2']))

    def create_contribution(self, contributor_id, repo_id):
        with self.driver.session() as session:
            # Write transactions allow the driver to handle retries and transient errors
            result = session.write_transaction(
                self._create_and_return_relation, contributor_id, "Person", repo_id, "Repository", "CONTRIBUTES_IN")
            for record in result:
                print("Created contribution between: {o1}, {o2}".format(
                    o1=record['o1'], o2=record['o2']))

    def create_following(self, follower_id, person_id):
        with self.driver.session() as session:
            # Write transactions allow the driver to handle retries and transient errors
            result = session.write_transaction(
                self._create_and_return_relation, follower_id, "Person", person_id, "Person", "FOLLOWS")
            for record in result:
                print("Created following between: {o1}, {o2}".format(
                    o1=record['o1'], o2=record['o2']))

    def create_review(self, person_id: int, repo_id: int, review_id: str):
        with self.driver.session() as session:
            # Write transactions allow the driver to handle retries and transient errors
            result = session.write_transaction(
                self._create_and_return_relation_with_id, person_id, "Person", repo_id, "Repository", "REVIEWS",review_id)
            for record in result:
                print("Created review between: {o1}, {o2} with id: {r}".format(
                    o1=record['o1'], o2=record['o2'],r=record['r']))
    
    def get_reviews_for_repo(self,repo_id):
        with self.driver.session() as session:
            query = (
            "MATCH (o1:Person)-[r:REVIEWS]->(o2:Repository { id: $repo_id }) "
            "RETURN r "
            )
            result = session.read_transaction(
                self._get_relation, query, repo_id=repo_id)
            for record in result:
                print("Found reviews {r} for repository {repo}".format(
                    r=record, repo=repo_id))
            return None if not result else result


    def get_review(self, person_id, repo_id):
        with self.driver.session() as session:
            query = (
            "MATCH (o1:Person { id: $o1_id })-[r:REVIEW]->(o2:Repository { id: $o2_id })"
            "RETURN r"
            )
            result = session.read_transaction(
                self._get_relation, query, o1_id=person_id, o2_id=repo_id)
            for record in result:
                print("Found review between: {o1}, {o2} with id: {r}".format(
                    o1=person_id, o2=repo_id,r=record))
            return None if not result else result[0]
    
    @staticmethod
    def _get_relation(tx, query, **kargs):
        # print(**kargs)
        result = tx.run(query, **kargs)
        try:
            return [record["r"]["id"] for record in result]
        # Capture any errors along with the query and data for traceability
        except ServiceUnavailable as exception:
            logging.error("{query} raised an error: \n {exception}".format(
                query=query, exception=exception))
            raise
    
    @staticmethod
    def _get_nodes(tx, query, *to_return, **kargs):
        # print(**kargs)
        result = tx.run(query, **kargs)
        try:
            response = []
            for record in result:
                response.append({})
                last_dict = response[-1]
                for object in to_return:
                    last_dict[object] = record[object]["id"]
            print(response)
            return response
        # Capture any errors along with the query and data for traceability
        except ServiceUnavailable as exception:
            logging.error("{query} raised an error: \n {exception}".format(
                query=query, exception=exception))
            raise

    def get_recommended_users(self,id: int, depth: int):
        with self.driver.session() as session:
            query = (
            "MATCH (o1:Person { id: $o1_id })-[r:FOLLOWS*1.." + str(depth) + "]-(o:Person)"
            "RETURN DISTINCT o"
            )
            result = session.read_transaction(
                self._get_nodes, query, "o", o1_id=id)
            for record in result:
                print("Found following user with id {p} for id {id}".format(
                    p=record["o"], id=id))
            # print(list(map(lambda elem: elem["o"],result)))
            print(len(result))
            return None if not result else list(map(lambda elem: elem["o"],result))

    def get_recommended_repos(self,id: int, depth: int):
        recommended_users_ids = self.get_recommended_users(id,depth)
        with self.driver.session() as session:
            query = (
                "MATCH (n:Person)-[:CONTRIBUTES_IN|:OWNS]-(r:Repository) WHERE ANY(user_id IN " + str(recommended_users_ids) + " WHERE user_id = n.id) AND NOT EXISTS{MATCH (p:Person {id: $u_id})-[:CONTRIBUTES_IN|:OWNS]-(:Repository {id: r.id})} "
                "RETURN DISTINCT r"
            )
            result = session.read_transaction(
                self._get_nodes, query, "r", u_id=id)
            for record in result:
                print("Found following user repos with id {r} where user with id {id} doesn't contribute/own".format(
                    r=record["r"], id=id))
            # print(list(map(lambda elem: elem["r"],result)))
            print(len(result))
            return None if not result else list(map(lambda elem: elem["r"],result))

    # @staticmethod
    # def _get_relation(tx, o1_id, o1_label, o2_id, o2_label, relation_label):
    #     query = (
    #         "MATCH (o1:" + o1_label + " { id: $o1_id })-[r:" + relation_label + "]->(o2:" + o2_label + " { id: $o2_id })"
    #         "RETURN r"
    #     )
    #     result = tx.run(query, o1_id=o1_id, o2_id=o2_id)
    #     try:
    #         return [record["r"]["id"] for record in result]
    #     # Capture any errors along with the query and data for traceability
    #     except ServiceUnavailable as exception:
    #         logging.error("{query} raised an error: \n {exception}".format(
    #             query=query, exception=exception))
    #         raise

mongo_client = MongoClient(27017)
neo_client = Neo4jClient(7687,'admin', 'admin')



