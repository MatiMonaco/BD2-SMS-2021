from fastapi import APIRouter, Body
from fastapi.encoders import jsonable_encoder
from server.models.status_code_enum import StatusCodeEnum
from server.database import mongo_client, neo_client
import json
from enum import Enum
from server.models.response_model_types import (
    ErrorResponseModel,
    ResponseModel,
    PaginatedResponseModel
)

with open("app/config.json") as file:
    config = json.load(file)
    server_url = config["server_url"]
    server_port = config["server_port"]

router = APIRouter()

class UserOrderBy(str, Enum):
    followers = "followers"
    following = "following"

@router.get("/", response_description="Users retrieved")
async def get_users(order_by: UserOrderBy = UserOrderBy.followers, asc: bool = False, page: int = 1, limit: int = 10):
    users, total_pages = await mongo_client.get_users(order_by.value, asc, page-1,limit)
    if users:
        return PaginatedResponseModel(users, page, limit, total_pages)
    return ResponseModel(users, "Empty list returned")

@router.get("/{username}/recommended/repos", response_description="Users retrieved")
async def get_recommended_repos(username: str, depth: int = 1, page: int = 1, limit: int = 10):
	user = await mongo_client.get_user(username)
	if user:
		recommended_ids = neo_client.get_recommended_repos(user['_id'], depth=depth+1)
		if recommended_ids:
			repo_reviews_dict = {}
			for repo_id in recommended_ids:
				reviews = neo_client.get_reviews_for_repo(repo_id)
				if not reviews:
					reviews = []
				print(reviews)
				repo_reviews_dict[repo_id] = reviews
			
			repos, total_pages = await mongo_client.get_repos_recommendations_by_id(user,recommended_ids, repo_reviews_dict, page-1, limit)
			return PaginatedResponseModel(repos, page, limit, total_pages)
		# Recomendar los repos mas populares
		else:
			# repos = await mongo_client.get_most_starred_repos(limit)
			return {"message": "No recommendations found", "most_starred_repos_url": f"http://{server_url}:{server_port}/repos/?order_by=stars&asc=false&page=1&limit=10"}
			# return ResponseModel(repos, "Most starred repositories")
	return {"message": "User not found"}


@router.get("/{username}/recommended/users", response_description="Retrieves recommended users for specified user")
async def get_recommended_users(username: str, depth: int = 1, page: int = 1, limit: int = 10):
	user = await mongo_client.get_user(username)
	if user:
		recommended_ids = neo_client.get_recommended_users(user['_id'], depth=depth+1)
		# TODO: ver qeu hacer si no hay ids recomendados
		if recommended_ids:
			users, total_pages = await mongo_client.get_user_recommendations_by_id(user,recommended_ids, page-1, limit)
			return PaginatedResponseModel(users, page, limit, total_pages)
		# Recomendar los usuarios mas populares
		else:
			# users = await mongo_client.get_most_popular_users(limit)
			# return ResponseModel(users, "Most followed users")
			return {"message": "No recommendations found", "most_followed_users_url": f"http://{server_url}:{server_port}/users/?order_by=followers&asc=false&page=1&limit=10"}
	return ResponseModel(user, "Empty list returned")
