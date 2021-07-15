from fastapi import FastAPI
from server.routes.repos import router as ReposRouter
from server.routes.users import router as UsersRouter
from pydantic import BaseModel, Field
from github import Github
from server.database import mongo_client, neo_client
import json
class UsernameSchema(BaseModel):
    username: str = Field(...)

with open("app/config.json") as file:
    config = json.load(file)
    github_api_token = config["github_api_token"]

app = FastAPI()


app.include_router(ReposRouter, tags=["Repos"], prefix="/repos")
app.include_router(UsersRouter, tags=["Users"], prefix="/users")
@app.get("/", tags=["Root"])
async def root():
    return {"message": "Hello World"}

@app.post("/register", tags=["User register"])
async def register(username: UsernameSchema):
    print("entre")
    mongo_user = await mongo_client.get_user(username.username)
    if not mongo_user:
        g = Github(github_api_token)
        # users = {}
        user = g.get_user(username.username)
        user_langs = set()
        for repo in user.get_repos():
            languages = list(repo.get_languages().keys())
            user_langs.update(languages)
        await mongo_client.insert_user(user_dict_helper(user, list(user_langs)))
        #     repo = await mongoClient.get_repo({"_id": int(repo.id)})
        #         #print(repo)
        #     if not repo:
        #         new_repo = await mongoClient.insert_repo({
        #                             'github_repo_id': repo.id,
        #                             'full_name': repo.full_name,
        #                             'name': repo.name,
        #                             'owner': repo.owner.url,
        #                             'stargazers_count': repo.stargazers_count,
        #                             'forks_count': repo.forks_count,
        #                             'created_at': str(repo.created_at),
        #                             'updated_at': str(repo.updated_at),
        #                             'languages': languages,
        #                             'html_url': repo.html_url,
        #                             'contributors_url': repo.contributors_url
        #                         })
        #         neoClient.create_ownership(item["owner"],repo.id)
                # for contributor in item["contributors"]:
                #     neoClient.create_contribution(contributor,item["github_repo_id"]) 
        # user = user_dict_helper(user)
        # to get the users the owner follows
        # if (user.following > 0):
        #     following = user.get_following()
        #     for i,follow in enumerate(following):
        #         if i > 10:
        #             break
        #         print(f"trying to create {follow.login} followed by {user.login}")
        #         next_depth = curr_depth+1
        #         if next_depth < max_depth:
        #             add_to_bds(users, follow, curr_depth+1)
        #             users[user.login]["following_user_ids"].append(follow.id)   
        return {"message": "Registered"}
    return {"message": "Not Found"}

# def add_to_bds(users, user, curr_depth, max_depth=2):
    
#     if user.login not in users and curr_depth <= max_depth:
#         print(f"creating user {user.login}")
#         users[user.login]={
#             "github_user_id": user.id,
#             "username": user.login,
#             "name": user.name,
#             "avatar_url": user.avatar_url,
#             "bio": user.bio,
#             "languages": [repo.language],
#             "following_user_ids": [],
#             "following": user.following,
#             "followers": user.followers,
#             "html_url": user.html_url
#         }

#         # to get the users the owner follows
#         if (user.following > 0):
#             following = user.get_following()
#             for i,follow in enumerate(following):
#                 if i > 10:
#                     break
#                 print(f"trying to create {follow.login} followed by {user.login}")
#                 next_depth = curr_depth+1
#                 if next_depth < max_depth:
#                     add_to_dict(users, follow, curr_depth+1)
#                     users[user.login]["following_user_ids"].append(follow.id)   

def user_dict_helper(user, user_langs):
    return {
            "github_user_id": user.id,
            "username": user.login,
            "name": user.name,
            "avatar_url": user.avatar_url,
            "bio": user.bio,
            "languages": user_langs,
            "following_user_ids": [],
            "following": user.following,
            "followers": user.followers,
            "html_url": user.html_url
        }