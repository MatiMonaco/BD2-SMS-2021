from app.server.models.response_model_types import PaginatedResponseModel
from fastapi import APIRouter, Body
from fastapi.encoders import jsonable_encoder
from app.server.database import mongo_client, neo_client
from app.server.models.status_code_enum import StatusCodeEnum
from enum import Enum
from app.server.models.response_model_types import (
    ErrorResponseModel,
    ResponseModel,
    # NewsSchema,
)

class ReviewOrderBy(str, Enum):
    created_at = "created_at"
    score = "score"

class RepoOrderBy(str, Enum):
    repo_name = "name"
    stars = "stars"
    created_at = "created_at"
    updated_at = "updated_at"
    forks_count = "forks_count"

router = APIRouter()
@router.get("/", response_description="Repos retrieved")
async def get_repos(order_by: RepoOrderBy = RepoOrderBy.created_at, asc: bool = False, page: int = 1, limit: int = 10):
    repos, total_pages = await mongo_client.get_repos(order_by.value, asc, page-1,limit)
    if repos:
        return PaginatedResponseModel(repos, page, limit, total_pages)
    return ResponseModel(repos, "Empty list returned")

@router.get("/{username}/{reponame}", response_description="Returns information asociated to the requested repository")
async def get_repo_by_name_and_username(username: str, reponame: str):
    repos = await mongo_client.get_repo(username, reponame)
    if repos:
        return ResponseModel(repos,  "Retrieved requested repository")
    #TODO: change to NOT FOUND, change message
    return ResponseModel(repos,  "Empty list returned")

@router.get("/{username}/{reponame}/reviews", response_description="Retrieved reviews for requested repository")
async def get_repo_reviews(username: str, reponame: str, order_by: ReviewOrderBy = ReviewOrderBy.created_at, asc: bool = False, page: int = 1, limit: int = 10):
    repo = await mongo_client.get_repo(username, reponame)
    if repo:
        repo_id = repo['_id']
        # reviews, total_pages = await mongo_client.get_repos(page,limit)
        review_ids = neo_client.get_reviews_for_repo(repo_id)
        if review_ids:
            reviews,total_pages = await mongo_client.get_reviews(review_ids,order_by.value,asc,page-1,limit)
            return PaginatedResponseModel(reviews,page,limit,total_pages)
    return ResponseModel(review_ids,  "Empty list returned")



