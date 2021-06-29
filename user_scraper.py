from time import sleep
from github import Github
from pprint import pprint
import json

g = Github('insert token here')
g.per_page = 100
query_count = 0
print(f"remaining queries: {g.rate_limiting[0]}")
users = {}


def add_to_dict(users, user, curr_depth, max_depth=2):
    if user.login not in users and curr_depth <= max_depth:
        print(f"creating user {user.login}")
        users[user.login]={
            "username": user.login,
            "name": user.name,
            "avatar_url": user.avatar_url,
            "bio": user.bio,
            "languages": [repo.language],
            "following": []
        }

        # to get the users the owner follows
        if (user.following > 0):
            following = user.get_following()
            for follow in following:
                print(f"trying to create {follow.login} followed by {user.login}")
                add_to_dict(users, follow, curr_depth+1)
                users[user.login]["following"].append(follow.login)


with open('resources/data.json', 'r') as file:
    data = json.load(file)
    for idx, item in enumerate(data):
        repo = g.get_repo(item['full_name'])
        query_count += 1
        print(repo.full_name)
        user = repo.owner

        if user.login in users:
            users[user.login]["languages"].append(repo.language) 
        else:
            add_to_dict(users, user, 1)

        for contributor in repo.get_contributors():
            add_to_dict(users, contributor, 1)



        if idx > 4:
            break # para salir del for y solo hacer los primeros 4 usuarios
    with open('users_4.json', 'w') as f:
        json.dump(users, f)
