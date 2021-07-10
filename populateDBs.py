import json
import asyncio
from app.server.database import MongoClient, Neo4jClient
from pprint import pprint
mongoClient = MongoClient(27017)
neoClient = Neo4jClient(7687,'admin', 'admin')

async def insert_data():
    with open('resources/updated_data.json', 'r') as repos_json:
        repo_data = json.load(repos_json)
           # Inserting repos
        for item in repo_data:
            repo = await mongoClient.get_repo({"_id": int(item["github_repo_id"])})
            #print(repo)
            if not repo:
                new_repo = await mongoClient.insert_repo(item)
                neoClient.create_ownership(item["owner"],item["github_repo_id"])
                for contributor in item["contributors"]:
                    neoClient.create_contribution(contributor,item["github_repo_id"]) 
    with open('resources/users.json', 'r') as users_json:
        user_data = json.load(users_json)
        # Inserting users
        for item in user_data.values():
            print(item)
            user = await mongoClient.get_user({"_id": int(item["github_user_id"])})
            #print(user)
            if not user:
                new_user = await mongoClient.insert_user(item)
                for following in item["following_user_ids"]:
                    neoClient.create_following(item["github_user_id"],following) 

if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(insert_data())
         