# import requests module
import requests
  
BASE_URL = 'https://api.github.com'
TOKEN = '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'
def get_user(username: str, headers: dict) -> dict:
    response = requests.get(BASE_URL + '/users/' + username)
    # print response
    print(response)
    
    # print json content
    print(response.json())
    return response

def search_repos(searched: str, parameters: dict) -> dict:
    response = requests.get(BASE_URL + '/search/' + searched, params=parameters)
    # print response
    print(response)
    # print json content
    print(response.json())
    return response

def get_following(url: str) -> dict:
    response = requests.get(url)
    return response

get_user('matimonaco', {'Authentication': 'token ' + TOKEN})
search_repos('repositories', {'q': 'stars:>1', 'sort':'stars', 'per_page': 100, 'page': 1})