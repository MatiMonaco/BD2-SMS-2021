from time import sleep
from github import Github
from pprint import pprint
import json

g = Github('Insert your token here')
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
            data.append({
                'full_name': repo.full_name,
                'name': repo.name,
                'owner': repo.owner.url,
                'stargazers_count': repo.stargazers_count,
                'forks_count': repo.forks_count,
                'created_at': str(repo.created_at),
                'updated_at': str(repo.updated_at),
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

with open('data.json', 'w') as outfile:
    json.dump(data, outfile)
print(len(data))
