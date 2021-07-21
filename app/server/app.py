from fastapi import FastAPI, Response, status
from app.server.routes.repos import router as ReposRouter
from app.server.routes.users import router as UsersRouter
from app.server.routes.reviews import router as ReviewsRouter
from pydantic import BaseModel, Field
from github import Github, GithubException
from app.server.database import mongo_client, neo_client
from app.config import config

class UsernameSchema(BaseModel):
    username: str = Field(...)


github_api_token = config['GITHUB_API_TOKEN']
app = FastAPI()


app.include_router(ReposRouter, tags=["Repos"], prefix="/repos")
app.include_router(UsersRouter, tags=["Users"], prefix="/users")
app.include_router(ReviewsRouter, tags=["Reviews"], prefix="/reviews")
@app.get("/", tags=["Root"])
async def root():
    return {"FastAPI": "https://bd2-sms.herokuapp.com/docs"}

@app.post("/register", tags=["User register"])
async def register(username: UsernameSchema, response: Response):
    g = Github(github_api_token)
    users = set()
    print("register username: "+username.username)
    user = g.get_user(username.username)
    ret = await add_user_rec(users, user,True,5,5, 0, 3)
    if ret:
        return {"message": "Registered"}
    else:
        response.status_code = status.HTTP_409_CONFLICT
        return {"message": "Conflict"}

@app.post("/populate_database", tags=["User register"])
async def populate_database(response: Response):
    g = Github(github_api_token)
    users = set()
 
    max_repos = 10
    popular_repos = g.search_repositories(f"stars:1..99999999", sort='stars', order='desc')
    count = 0
    for repo in popular_repos:
        
        user = repo.owner
        print(f"Registering user: {repo.owner.login}")
        await add_user_rec(users, user,True,5,5, 0, 3)
        count+=1
        if count >= max_repos:
                break

  
    return {"message": f"Registered {count} users"}





async def add_user_rec(users, user, register,max_following,max_repos,curr_depth, max_depth=3):
        mongo_user = await mongo_client.get_user(user.login)
        registered = False
        if mongo_user:
            registered =  mongo_user['registered'] 
        if not registered and not user.id in users:
            print(f"creating user {user.login}")
            user_langs = set()
            users.add(user.id)
            for i,item in enumerate(user.get_repos(sort='updated')):
                if i > max_repos:
                    break
              
                fullname = item.full_name.split('/')
                print(fullname[0] + " - "+fullname[1])
                repo = await mongo_client.get_repo(fullname[0], fullname[1])
                if not repo:
                    repo_langs = {}
                    try:
                        repo_langs = list(item.get_languages().keys())
                        user_langs.update(repo_langs)
                    except GithubException as e:
                        continue
                    repo_dict = repo_dict_helper(item,repo_langs)
                    if curr_depth <= max_depth:
                        await mongo_client.insert_repo(repo_dict)
                        neo_client.create_ownership(user.id,repo_dict["github_repo_id"])

            #add user to mongo
            if mongo_user:
                if not registered and register:
                    await mongo_client.set_registered(user.id,True)
            else:
                await mongo_client.insert_user(user_dict_helper(user,list(user_langs),register))
            

            if curr_depth < max_depth:
            # to get the users the owner follows
                if (user.following > 0):
                    following = user.get_following()
                    for i,follow in enumerate(following):
                        if i > max_following:
                            break
                        print(f"trying to create {follow.login} followed by {user.login}")
                        neo_client.create_following(user.id,follow.id) 
                        await add_user_rec(users, follow,False,5,5, curr_depth+1,max_depth)
            return True
        else:
            return False

            

def user_dict_helper(user, user_langs,register):
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
            "html_url": user.html_url,
            "registered":register
            
        }

        
def repo_dict_helper(repo, repo_langs):
    return {
            'github_repo_id': repo.id,
            'full_name': repo.full_name,
            'name': repo.name,
            'owner': repo.owner.url,
            'stargazers_count': repo.stargazers_count,
            'forks_count': repo.forks_count,
            'created_at': str(repo.created_at),
            'updated_at': str(repo.updated_at),
            'languages': repo_langs,
            'html_url': repo.html_url,
            'contributors_url': repo.contributors_url
        }
