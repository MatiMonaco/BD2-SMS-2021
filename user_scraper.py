from time import sleep
from github import Github
from pprint import pprint
import json

g = Github('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')
g.per_page = 100
query_count = 0
print(f"remaining queries: {g.rate_limiting[0]}")
users = {}


def add_to_dict(users, user, curr_depth, max_depth=2):
    
    if user.login not in users and curr_depth <= max_depth:
        print(f"creating user {user.login}")
        users[user.login]={
            "github_user_id": user.id,
            "username": user.login,
            "name": user.name,
            "avatar_url": user.avatar_url,
            "bio": user.bio,
            "languages": [repo.language],
            "following_user_ids": [],
            "following": user.following,
            "followers": user.followers,
            "html_url": user.html_url
        }

        # to get the users the owner follows
        if (user.following > 0):
            following = user.get_following()
            for i,follow in enumerate(following):
                if i > 10:
                    break
                print(f"trying to create {follow.login} followed by {user.login}")
                next_depth = curr_depth+1
                if next_depth < max_depth:
                    add_to_dict(users, follow, curr_depth+1)
                    users[user.login]["following_user_ids"].append(follow.id)   


with open('resources/data.json', 'r') as file:
    data = json.load(file)
    with open('resources/updated_data.json', 'w') as updated_file:
        updated_data = []
        for idx, item in enumerate(data):
            repo = g.get_repo(item['full_name'])
            query_count += 1
            print(repo.full_name)
            user = repo.owner

            if user.login in users:
                users[user.login]["languages"].append(repo.language) 
            else:
                add_to_dict(users, user, 1)
            print("NOW contributors")
            contributors = []
            for i,contributor in enumerate(repo.get_contributors()):
                if i > 5:
                    break
                add_to_dict(users, contributor, 1)
                contributors.append(contributor.id)
            new_data = {
                "github_repo_id": item["github_repo_id"],
                "full_name": item["full_name"],
                "name": item["name"],
                "owner": user.id,
                "stargazers_count": item["stargazers_count"],
                "forks_count": item["forks_count"],
                "created_at": item["created_at"],
                "updated_at": item["updated_at"],
                "html_url": item["html_url"],
                "languages": item["languages"],
                "contributors": contributors
            }
            updated_data.append(new_data)
            if idx > 4:
                break # para salir del for y solo hacer los primeros 6 repos
        json.dump(updated_data, updated_file)
with open('resources/users.json', 'w') as f:
    json.dump(users, f)
