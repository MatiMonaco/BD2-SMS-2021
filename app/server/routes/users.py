from fastapi import APIRouter, Body
from fastapi.encoders import jsonable_encoder
from server.models.status_code_enum import StatusCodeEnum
from server.database import mongo_client, neo_client

from server.models.response_model_types import (
    ErrorResponseModel,
    ResponseModel,
    PaginatedResponseModel
)

router = APIRouter()


@router.get("/{username}/recommended/repos", response_description="Users retrieved")
async def get_recommended_repos(username: str, depth: int = 1, page: int = 1, limit: int = 10):
	user = await mongo_client.get_user(username)
	if user:
		recommended_ids = neo_client.get_recommended_repos(user['_id'], depth=depth)
		repos, total_pages = await mongo_client.get_repos_recommendations_by_id(user,recommended_ids, page-1, limit)
		return PaginatedResponseModel(repos, page, limit, total_pages)
	return ResponseModel(user, StatusCodeEnum.OK.value, "Empty list returned")


@router.get("/{username}/recommended/users", response_description="Retrieves recommended users for specified user")
async def get_recommended_users(username: str, depth: int = 1, page: int = 1, limit: int = 10):
	user = await mongo_client.get_user(username)
	if user:
		recommended_ids = neo_client.get_recommended_users(user['_id'], depth=depth)
		users, total_pages = await mongo_client.get_user_recommendations_by_id(user,recommended_ids, page-1, limit)
		return PaginatedResponseModel(users, page, limit, total_pages)
	return ResponseModel(user, StatusCodeEnum.OK.value, "Empty list returned")
