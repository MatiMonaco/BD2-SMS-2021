import motor.motor_asyncio
from neo4j import GraphDatabase
import logging
from bson.objectid import ObjectId
from neo4j.exceptions import ServiceUnavailable
from fastapi.encoders import jsonable_encoder
import math
import json
import time
from datetime import datetime
import os
from app.config import config


server_host = config['SERVER_HOST']
server_port = config['PORT']
# mongodb


def normalize_data(data, max):
    # if max-min == 0: return 0
    return float(data)/float(max) if max != 0 else 0



class MongoClient:
    def __init__(self):
        #TODO: crear indice en fullname 
   
        self.mongo_client = motor.motor_asyncio.AsyncIOMotorClient(config['MONGO_DETAILS'])
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
            'registered': user_data['registered']
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

    async def set_registered(self,user_id,registered):
            user = await self.users_collection.update_one({"_id":user_id},{"$set":{"registered":registered}})
            new_user = await self.users_collection.find_one({"_id": user_id})
            return new_user

    
    async def insert_review(self,review_data: dict):
        review_data['created_at'] = str(datetime.now().isoformat(" ", "seconds"))
        review = await self.reviews_collection.insert_one(MongoClient._review_helper(review_data))
        new_review = await self.reviews_collection.find_one({"_id": review.inserted_id})
        new_review['_id'] = str(new_review['_id'])
        return new_review

    async def get_repos(self, order_by: str, asc: bool, page: int, limit: int):
        repos = []
        total = await self.repos_collection.count_documents({})
        total_pages = math.ceil(total/limit)
        asc_val = 1 if asc else -1
        async for repo in self.repos_collection.find(sort=[(order_by,asc_val)],skip=page*limit, limit=limit):
            full_name = repo['full_name'].split('/')
            repo['reviews_url'] = f"http://{server_host}:{server_port}/repos/{full_name[0]}/{full_name[1]}/reviews"
            repos.append(repo)
        return repos,total_pages, total

    async def get_repo(self, username: str, reponame: str):
        full_name = username + '/' + reponame
        repo = await self.repos_collection.find_one({'full_name': {'$regex': '^{}$'.format(full_name),'$options': 'i'}})
        if repo:
            repo['reviews_url'] = f"http://{server_host}:{server_port}/repos/{username}/{reponame}/reviews"
        return repo

    async def get_repo_by_id(self, repo_id):
        repo = await self.repos_collection.find_one({'_id': repo_id})
        return repo


    async def get_user(self, username: str):
        user = await self.users_collection.find_one({'username': username})
        return user

    async def update_user(self, id:str, data: dict):
        updated_user = await self.users_collection.update_one({"_id": id}, {"$set": data})
        if updated_user:
            return True
        return False

    async def update_repo(self, id:str, data: dict):
        updated_repo = await self.repos_collection.update_one({"_id": id}, {"$set": data})
        if updated_repo:
            return True
        return False

    async def update_review(self, id:str, data: dict):
        review = await self.reviews_collection.find_one({"_id": id})
        data['modified_at'] = str(datetime.now().isoformat(" ", "seconds"))
        review.update(data)
        
        updated_review = await self.reviews_collection.update_one({"_id": id}, {"$set": review})
        if updated_review:
            return True
        return False

    async def delete_review(self, id:str):
        review = await self.reviews_collection.delete_one({"_id": ObjectId(id)})
        if review:
            return True
        return False

        

    async def get_users(self, order_by: str, asc: bool, page: int, limit: int):
        users = []
        total = await self.users_collection.count_documents({})
        total_pages = math.ceil(total/limit)
        asc_val = 1 if asc else -1
        async for user in self.users_collection.find(sort=[(order_by,asc_val)],skip=page*limit, limit=limit):
            users.append(user)
        return users,total_pages, total

    async def get_users_by_id(self, user_ids: list, order_by: str, asc: bool, page: int, limit: int):
        users = []
        total = await self.users_collection.count_documents({"_id": {"$in": user_ids}})
        total_pages = math.ceil(total/limit)
        asc_val = 1 if asc else -1
        pipeline = [
            {"$match": 
                {"_id": {"$in": user_ids}}
            },
            {"$sort": {order_by: asc_val}},
            {"$skip": page*limit},
            {"$limit": limit}
        ]
        async for user in self.users_collection.aggregate(pipeline):
            users.append(user)
        return users,total_pages, total
    
    async def get_avg_reviews_rating(self,review_ids: list):
        if not review_ids:
            return None
        review_ids = [ObjectId(id) for id in review_ids]
        pipeline = [
            {"$match": 
                {"_id": {"$in": review_ids}}
            },
            { "$group": {
                    "_id": None,
                    "avg_score": {"$avg": "$score"}
                }
            },
            { "$project" : {
                    "_id": 0, 
                    "avg_score": 1
                } 
            }
        ]
        async for review in self.reviews_collection.aggregate(pipeline):
            return review['avg_score']
        return 0


    #TODO: calcular max languajes coincidentes
    async def get_repos_recommendations_by_id(self, user: dict, repo_ids: list, page: int, limit: int):
        repos = []
        total = await self.repos_collection.count_documents({"_id": {"$in": repo_ids}})

        max_pipeline = [
            {"$match": 
                {"_id": {"$in": repo_ids}}
            },
            {"$group": {
                    "_id": None,
                    "max_stars": {"$max": "$stars"},
                    "max_forks": {"$max": "$forks_count"},
                    "max_languages": {"$max": {"$size": "$languages"}},
                    "max_updated_at": {"$max": {"$toDouble": {"$toDate": "$updated_at"}}},
                }
            }
        ]
        max_stars, max_forks, max_langs, max_update = 0, 0, 0, 0
        max_avg_rating = 5
        async for maximum_vals in self.repos_collection.aggregate(max_pipeline):
            max_stars = maximum_vals['max_stars']
            max_forks = maximum_vals['max_forks']
            max_langs = maximum_vals['max_languages']
            max_update = maximum_vals['max_updated_at']
        
        total_pages = math.ceil(total/limit)
        user_langs = user['languages']
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
                    "avg_rating": { "$ifNull": [ "$avg_rating", None] },
                    "score" : {
                        "$sum" : [
                            {"$multiply": 
                                [
                                    { "$cond": [ { "$eq": [ max_update, 0 ] }, 0, {"$divide":[{"$toDouble": {"$toDate": "$updated_at"}}, max_update]} ] },0.2
                                ]
                            },
                            {"$multiply": 
                                [
                                    { "$cond": [ { "$eq": [ max_stars, 0 ] }, 0, {"$divide":["$stars", max_stars]} ] },0.3
                                ]
                            },
                            {"$multiply":
                                [
                                    { "$cond": [ { "$eq": [ max_forks, 0 ] }, 0, {"$divide":["$forks_count", max_forks]} ] },0.05
                                ]
                            },
                            {"$multiply":
                                [
                                    {"$divide":[{ "$ifNull": [ "$avg_rating", 0 ] }, max_avg_rating]}, 0.1
                                ]
                            },
                            {"$multiply": 
                                [
                                    { "$cond": [ { "$eq": [ max_langs, 0 ] }, 0, {"$divide":[{
                                        "$size": {
                                            "$filter": {
                                                "input": "$languages",
                                                "cond": {"$in": ["$$this",user_langs]}
                                            }
                                        }
                                    }, max_langs]} ] },0.35
                                ]
                            },
                        ]
                    }
                } 
            }, 
            {"$sort" : {"score" : -1} },
            {"$skip": page*limit},
            {"$limit": limit}
        ]
        async for repo in self.repos_collection.aggregate(pipeline):
            full_name = repo['full_name'].split('/')
            repo['reviews_url'] = f"http://{server_host}:{server_port}/repos/{full_name[0]}/{full_name[1]}/reviews"     
            repos.append(repo)
        return repos, total_pages, total

    #TODO: calcular todos los maximos en funcion de los maximos de todos los users y normalizar en el pipeline de aggregation en funcion de eso   
    async def get_user_recommendations_by_id(self, user: dict, user_ids: list, page: int, limit: int):
        users = []
        total = await self.users_collection.count_documents({"_id": {"$in": user_ids}})
        max_pipeline = [
            {"$match": 
                {"_id": {"$in": user_ids}}
            },
            {"$group": {
                    "_id": None,
                    "max_followers": {"$max": "$followers"},
                    "max_languages": {"$max": {"$size": "$languages"}},
                }
            }
        ]
        max_followers, max_langs = 0, 0
        async for maximum_vals in self.users_collection.aggregate(max_pipeline):
            max_followers = maximum_vals['max_followers']
            max_langs = maximum_vals['max_languages']
        
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
                        [
                            { "$cond": [ { "$eq": [ max_followers, 0 ] }, 0, {"$divide":["$followers", max_followers]} ] },0.6
                        ]
                    },
                    {"$multiply":
                        [
                            { "$cond": [ { "$eq": [ max_langs, 0 ] }, 0, {"$divide":[{
                                "$size": {
                                    "$filter": {
                                        "input": "$languages",
                                        # "as": "lang",
                                        "cond": {"$in": ["$$this",user_langs]}
                                    }
                                }
                            }, max_langs]} ] },0.4
                        ]
                    },
                ]
            }
            } 
            }, 
            {"$sort" : {"score" : -1} },
            {"$skip": page*limit},
            {"$limit": limit}
        ]
        async for rec_user in self.users_collection.aggregate(pipeline):
            users.append(rec_user)
        return users, total_pages, total

    async def get_user(self, username: str):
        user = await self.users_collection.find_one({'username': {'$regex': '^{}$'.format(username),'$options': 'i'}})
        return user

    async def get_review(self, review_id: str):
        review = await self.reviews_collection.find_one({'_id': ObjectId(review_id)})
        return review

    async def get_reviews(self, review_ids: list, order_by: str, asc: bool, page: int, limit: int):
        reviews = []
        total = await self.reviews_collection.count_documents({})
        total_pages = math.ceil(total/limit)
        review_ids = [ObjectId(id) for id in review_ids]
        asc_val = 1 if asc else -1
        async for review in self.reviews_collection.find({"_id": {"$in": review_ids}},sort=[(order_by,asc_val)],skip=page*limit, limit=limit):
            review['_id'] = str(review['_id'])
            reviews.append(review)
        return reviews,total_pages

    async def get_reviews_with_repo(self, review_dict: dict, order_by: str, asc: bool, page: int, limit: int):
        reviews = []
        total = await self.reviews_collection.count_documents({})
        total_pages = math.ceil(total/limit)
        review_ids = [ObjectId(id) for id in list(review_dict.keys())]
        asc_val = 1 if asc else -1
        async for review in self.reviews_collection.find({"_id": {"$in": review_ids}},sort=[(order_by,asc_val)],skip=page*limit, limit=limit):
            review['_id'] = str(review['_id'])
            repo = await self.repos_collection.find_one({"_id": review_dict[review['_id']]})
            review['repo_name'] = repo['full_name']
            reviews.append(review)
        return reviews,total_pages, total


# neo4j

class Neo4jClient:

    def __init__(self):
     
        self.driver = GraphDatabase.driver(config['NEO4J_DETAILS'],auth=(config['NEO4J_USER'],config['NEO4J_PASS']))
      

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

    def create_contribution(self, contributor_id, repo_id):
        with self.driver.session() as session:
            # Write transactions allow the driver to handle retries and transient errors
            result = session.write_transaction(
                self._create_and_return_relation, contributor_id, "Person", repo_id, "Repository", "CONTRIBUTES_IN")

    def create_following(self, follower_id, person_id):
        with self.driver.session() as session:
            # Write transactions allow the driver to handle retries and transient errors
            result = session.write_transaction(
                self._create_and_return_relation, follower_id, "Person", person_id, "Person", "FOLLOWS")
            return result




    def create_review(self, person_id: int, repo_id: int, review_id: str):
        with self.driver.session() as session:
            # Write transactions allow the driver to handle retries and transient errors
            result = session.write_transaction(
                self._create_and_return_relation_with_id, person_id, "Person", repo_id, "Repository", "REVIEWS",review_id)
    
    def get_reviews_for_repo(self,repo_id):
        with self.driver.session() as session:
            query = (
            "MATCH (o1:Person)-[r:REVIEWS]->(o2:Repository { id: $repo_id }) "
            "RETURN r "
            )
            result = session.read_transaction(
                self._get_relation, query, repo_id=repo_id)
            return None if not result else result

    def get_repo_by_review(self, review_id):
        with self.driver.session() as session:
            query = (
                "MATCH (o1:Person)-[r {id: $review_id}]->(o:Repository) "
            "RETURN o"
            )
            result = session.read_transaction(
                self._get_nodes, query, "o", review_id=review_id)
            return None if not result else result[0]["o"]



    def get_reviews_for_user(self,user_id):
        with self.driver.session() as session:
            # I'd like to get the review AND it's corresponding repo
            query = (
            "MATCH (o1:Person {id: $user_id})-[r:REVIEWS]->(o2:Repository)"
            "RETURN r,o2"
            )
            result = session.run(query, user_id=user_id)
            results = {}
            for record in result:
                review = record["r"]["id"]
                repo = record["o2"]["id"]
                results[review] = repo
            return None if not result else results

    def has_review(self, reviewer_id: int, repo_id: int):
        with self.driver.session() as session:
            query = (
            "MATCH (o1:Person { id: $o1_id })-[r:REVIEWS]->(o2:Repository {id: $o2_id})"
            "RETURN count(r)"
            )
            result = session.run(query, o1_id=reviewer_id, o2_id=repo_id)
            return result.single().value() >= 1

    
    @staticmethod
    def _get_relation(tx, query, **kargs):
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
        result = tx.run(query, **kargs)
        try:
            response = []
            for record in result:
                response.append({})
                last_dict = response[-1]
                for object in to_return:
                    last_dict[object] = record[object]["id"]
            return response
        # Capture any errors along with the query and data for traceability
        except ServiceUnavailable as exception:
            logging.error("{query} raised an error: \n {exception}".format(
                query=query, exception=exception))
            raise
    
    # TODO: Deberia buscar todos los usuarios en la profundidad especificada menos los usuarios en la profundidad 1 ya que esos usuarios ya son seguidos 
    def get_recommended_users(self,id: int, depth: int):
        with self.driver.session() as session:
            query = (
            "MATCH (o1:Person { id: $o1_id })-[r:FOLLOWS*2.." + str(depth) + "]->(o:Person)"
            "WHERE NOT EXISTS {MATCH (:Person { id: o1.id })-[r1:FOLLOWS]->(:Person {id: o.id})} AND o1.id <> o.id "
            "RETURN DISTINCT o"
            )
            result = session.read_transaction(
                self._get_nodes, query, "o", o1_id=id)
            return [] if not result else list(map(lambda elem: elem["o"],result))

    def get_followed_users(self,id: int):
        with self.driver.session() as session:
            query = (
            "MATCH (o1:Person { id: $o1_id })-[r:FOLLOWS]->(o:Person)"
            "RETURN DISTINCT o"
            )
            result = session.read_transaction(
                self._get_nodes, query, "o", o1_id=id)
            return [] if not result else list(map(lambda elem: elem["o"],result))

    def is_following(self, user_id: int, other_user_id: int):
        with self.driver.session() as session:
            query = (
            "MATCH (o1:Person { id: $o1_id })-[r:FOLLOWS]->(o2:Person {id: $o2_id})"
            "RETURN count(r)"
            )
            result = session.run(query, o1_id=user_id, o2_id=other_user_id)
            return result.single().value() >= 1

    def delete_following(self, follower_id, person_id):
        with self.driver.session() as session:
            query = (
            "MATCH (o1:Person { id: $o1_id })-[r:FOLLOWS]->(o2:Person {id: $o2_id})"
            "DELETE r"
            )
            result = session.run(query, o1_id=follower_id, o2_id=person_id)
            return result

    def delete_review(self, review_id):
        with self.driver.session() as session:
            query = (
            "MATCH (o1:Person)-[r:REVIEWS { id: $id }]-(o2:Repository)"
            "DELETE r"
            )
            result = session.run(query, id=review_id)
            return result


    def get_followed_by_users(self,id: int):
        with self.driver.session() as session:
            query = (
            "MATCH (o:Person)-[r:FOLLOWS]->(o1:Person { id: $o1_id })"
            "RETURN DISTINCT o"
            )
            result = session.read_transaction(
                self._get_nodes, query, "o", o1_id=id)
            return [] if not result else list(map(lambda elem: elem["o"],result))

    def get_recommended_repos(self,id: int, depth: int):
        recommended_users_ids = self.get_recommended_users(id,depth)
        with self.driver.session() as session:
            query = (
                "MATCH (n:Person)-[:CONTRIBUTES_IN|:OWNS]-(r:Repository) WHERE ANY(user_id IN " + str(recommended_users_ids) + " WHERE user_id = n.id) AND NOT EXISTS{MATCH (p:Person {id: $u_id})-[:CONTRIBUTES_IN|:OWNS]-(:Repository {id: r.id})} "
                "RETURN DISTINCT r"
            )
            result = session.read_transaction(
                self._get_nodes, query, "r", u_id=id)
            return [] if not result else list(map(lambda elem: elem["r"],result))


mongo_client = MongoClient()
neo_client = Neo4jClient()



