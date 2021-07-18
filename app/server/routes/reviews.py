from server.models.response_model_types import PaginatedResponseModel
from server.models.review import ReviewSchema, UpdateReviewModel, DeleteReviewModel
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
    modified_at = "modified_at"
    score = "score"

router = APIRouter()

@router.put("/{review_id}", response_description="Edit a review")
async def edit_review(review_id: str, req: UpdateReviewModel = Body(...)):
    req = {k:v for k, v in req.dict().items() if v is not None}
    review = await mongo_client.get_review(review_id)
    if review:
        updated_review = await mongo_client.update_review(review['_id'], req)
        if updated_review:
            return ResponseModel("Review update", "Review updated successfully")
        else:
            return ErrorResponseModel("An error ocurred", 500, "There was an error updating the review data")
    else:
        return ErrorResponseModel("Not found", 404, "Review not found")

# Create new review
@router.post("/", response_description="Create new review")
async def post_repo_review(req: ReviewSchema = Body(...)):
    req = {k:v for k, v in req.dict().items() if v is not None}
    username, reponame = req['repo_name'].split('/', 1)
    reviewer = await mongo_client.get_user(req['reviewer'])
    repo = await mongo_client.get_repo(username,reponame)
    if not reviewer:
        return ErrorResponseModel("Not found", 404, "User not found")
    if not repo:
        return ErrorResponseModel("Not found", 404, "Repository not found")

    # Check if
    relation = neo_client.has_review(reviewer['_id'],repo['_id'])
    if not relation:
        new_review = await mongo_client.insert_review(req)
        if new_review:
            new_relation = neo_client.create_review(reviewer['_id'],repo['_id'], str(new_review['_id']))
            return ResponseModel(new_review, "Successfully created new review")
        else:
            return ErrorResponseModel("An error ocurred", 500, "There was an error updating the review data")
    #TODO: change to apropiate response in failure
    return ErrorResponseModel("Unprocessable Entity", 422, "Review already exists for this user in this repo")

@router.delete("/{review_id}", response_description="Delete review")
async def post_repo_review(review_id: str):
    review = await mongo_client.get_review(review_id)
    if review:
        deleted_relation = neo_client.delete_review(review_id)
        deleted_review = mongo_client.delete_review(review_id)

        if not deleted_relation or not deleted_review:
            return ErrorResponseModel("An error ocurred", 500, "There was an error updating the review data")
        else:
            return ResponseModel("Review delete", "Review deleted successfully")
    else:
        return ErrorResponseModel("Not found", 404, "Review not found")
