from app.server.models.review import ReviewSchema, UpdateReviewModel 
from typing import Optional
from fastapi import APIRouter, Body
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
    modified_at = "modified_at"
    score = "score"

router = APIRouter()


# Create new review
@router.post("/", response_description="Create new review")
async def post_repo_review(response: Response, req: ReviewSchema = Body(...)):
    req = {k:v for k, v in req.dict().items() if v is not None}
    username, reponame = req['repo_name'].split('/', 1)
    reviewer = await mongo_client.get_user(req['reviewer'])
    repo = await mongo_client.get_repo(username,reponame)
    if not reviewer:
        response.status_code = status.HTTP_404_NOT_FOUND
        return ErrorResponseModel("Not found", 404, "User not found")
    if not repo:
        response.status_code = status.HTTP_404_NOT_FOUND
        return ErrorResponseModel("Not found", 404, "Repository not found")

    relation = neo_client.has_review(reviewer['_id'],repo['_id'])
    if not relation:
        new_review = await mongo_client.insert_review(req)
        if new_review:
            new_relation = neo_client.create_review(reviewer['_id'],repo['_id'], str(new_review['_id']))
            review_ids = neo_client.get_reviews_for_repo(repo['_id'])
            new_rating = await mongo_client.get_avg_reviews_rating(review_ids)
            # update repo average
            repo['avg_rating'] = new_rating
            updated_repo = await mongo_client.update_repo(repo['_id'], repo)
            if updated_repo:
                return ResponseModel(new_review, "Successfully created new review")
            else:
                response.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
                return ErrorResponseModel("An error ocurred", 500, "There was an error updating the review data")
        else:
            response.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
            return ErrorResponseModel("An error ocurred", 500, "There was an error updating the review data")
    #TODO: change to apropiate response in failure
    response.status_code = status.HTTP_409_CONFLICT
    return ErrorResponseModel("Conflict", 409, "Review already exists for this user in this repo")

@router.put("/{review_id}", response_description="Edit a review")
async def edit_review(response: Response, review_id: str, req: UpdateReviewModel = Body(...)):
    req = {k:v for k, v in req.dict().items() if v is not None}
    review = await mongo_client.get_review(review_id)
    repo_id = neo_client.get_repo_by_review(review_id)
    if review:
        updated_review = await mongo_client.update_review(review["_id"], req)
        # get repo
        repo = await mongo_client.get_repo_by_id(repo_id)
        # get review ids
        review_ids = neo_client.get_reviews_for_repo(repo["_id"])
        # get average score
        new_rating = await mongo_client.get_avg_reviews_rating(review_ids)
        # update repo
        repo['avg_rating'] = new_rating
        updated_repo = await mongo_client.update_repo(repo["_id"], repo)
        if updated_review and updated_repo:
            return ResponseModel("Review update", "Review updated successfully")
        else:
            response.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
            return ErrorResponseModel("An error ocurred", 500, "There was an error updating the review data")
    else:
        response.status_code = status.HTTP_404_NOT_FOUND
        return ErrorResponseModel("Not found", 404, "Review not found")

@router.delete("/{review_id}", response_description="Delete review")
async def post_repo_review(response: Response, review_id: str):
    review = await mongo_client.get_review(review_id)
    repo_id = neo_client.get_repo_by_review(review_id)
    if review:
        deleted_relation = neo_client.delete_review(review_id)
        deleted_review = await mongo_client.delete_review(review_id)
        # get repo
        repo = await mongo_client.get_repo_by_id(repo_id)
        # get review ids
        review_ids = neo_client.get_reviews_for_repo(repo['_id'])
        # get average score
        new_rating = await mongo_client.get_avg_reviews_rating(review_ids)
        # update repo
        repo['avg_rating'] = new_rating
        updated_repo = await mongo_client.update_repo(repo['_id'], repo)

        if not deleted_relation or not deleted_review or not updated_repo:
            response.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
            return ErrorResponseModel("An error ocurred", 500, "There was an error updating the review data")
        else:
            return ResponseModel("Review delete", "Review deleted successfully")
    else:
        response.status_code = status.HTTP_404_NOT_FOUND
        return ErrorResponseModel("Not found", 404, "Review not found")
