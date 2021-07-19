from time import sleep
from github import Github
from pprint import pprint
import json

# with open("app/config.json") as file:
#     config = json.load(file)
github_api_token = process.env.GITHUB_API_TOKEN
g = Github(github_api_token)
g.per_page = 100
print(g.rate_limiting)

amount_of_queries = 3
last_max = 325520
data = []
count = 0
for q in range(0, amount_of_queries):
    print(f"query number: {q}")
    repos = g.search_repositories(f"stars:1..{last_max - 1}", sort='stars', order='desc')
    try:
        for repo in repos:
            languages = list(repo.get_languages().keys())
            data.append({
                'github_repo_id': repo.id,
                'full_name': repo.full_name,
                'name': repo.name,
                'owner': repo.owner.url,
                'stargazers_count': repo.stargazers_count,
                'forks_count': repo.forks_count,
                'created_at': str(repo.created_at),
                'updated_at': str(repo.updated_at),
                'languages': languages,
                'html_url': repo.html_url,
                'contributors_url': repo.contributors_url
            })
            count += 1
            print(f"processed: {count}")
            last_max = repo.stargazers_count
    except Exception as e:
        print(e)
        print("Ups hice mierda el limite")
    sleep(60)

with open('resources/data.json', 'w') as outfile:
    json.dump(data, outfile)
print(len(data))
