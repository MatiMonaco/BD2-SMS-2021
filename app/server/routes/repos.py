from server.models.response_model_types import PaginatedResponseModel
from server.models.review import ReviewSchema
from typing import Optional
from fastapi import APIRouter, Body
from fastapi.encoders import jsonable_encoder
from server.database import mongo_client, neo_client
from server.models.status_code_enum import StatusCodeEnum
from enum import Enum
from server.models.response_model_types import (
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
async def get_repos(order_by: RepoOrderBy = RepoOrderBy.created_at, asc: bool = False, page: int = 0, limit: int = 10):
    repos, total_pages = await mongo_client.get_repos(order_by.value, asc, page,limit)
    if repos:
        return PaginatedResponseModel(repos, page, limit, total_pages)
    return ResponseModel(repos, StatusCodeEnum.OK.value, "Empty list returned")

@router.get("/{username}/{reponame}", response_description="Returns information asociated to the requested repository")
async def get_repo_by_name_and_username(username: str, reponame: str):
    repos = await mongo_client.get_repo(username, reponame)
    if repos:
        return ResponseModel(repos, StatusCodeEnum.OK.value, "Retrieved requested repository")
    #TODO: change to NOT FOUND, change message
    return ResponseModel(repos, StatusCodeEnum.OK.value, "Empty list returned")

@router.get("/{username}/{reponame}/review", response_description="Retrieved reviews for requested repository")
async def get_repo_reviews(username: str, reponame: str, order_by: ReviewOrderBy = ReviewOrderBy.created_at, asc: bool = False, page: int = 0, limit: int = 10):
    repo = await mongo_client.get_repo(username, reponame)
    if repo:
        repo_id = repo['_id']
        # reviews, total_pages = await mongo_client.get_repos(page,limit)
        review_ids = neo_client.get_reviews_for_repo(repo_id)
        if review_ids:
            reviews,total_pages = await mongo_client.get_reviews(review_ids,order_by.value,asc,page,limit)
            return PaginatedResponseModel(reviews,page,limit,total_pages)
    return ResponseModel(review_ids, StatusCodeEnum.OK.value, "Empty list returned")


# Create new review
@router.post("/{username}/{reponame}/review", response_description="Create new review")
async def post_repo_review(username: str, reponame: str, review: ReviewSchema):
    review = review.dict()
    reviewer = await mongo_client.get_user(review['reviewer'])
    repo = await mongo_client.get_repo(username,reponame)
    if reviewer and repo:
        relation = neo_client.get_review(reviewer['_id'],repo['_id'])
        if not relation:
            new_review = await mongo_client.insert_review(review)
            if new_review:
                new_relation = neo_client.create_review(reviewer['_id'],repo['_id'], str(new_review['_id']))
                return ResponseModel(new_review, StatusCodeEnum.OK.value, "Successfully created new review")
    #TODO: change to apropiate response in failure
    return ResponseModel([], StatusCodeEnum.BAD_REQUEST.value, "Bad request")

