from fastapi import APIRouter, Body, status, Response
from fastapi.encoders import jsonable_encoder
from app.server.models.status_code_enum import StatusCodeEnum
from app.server.database import mongo_client, neo_client
import json
from enum import Enum
from app.server.models.response_model_types import (

    ResponseModel,
    PaginatedResponseModel
)
from app.server.models.user import UserSchema, UpdateUserModel
from app.config import config

server_host = config['SERVER_HOST']
server_port = config['PORT']
router = APIRouter()

class UserOrderBy(str, Enum):
    followers = "followers"
    following = "following"

class ReviewOrderBy(str, Enum):
    created_at = "created_at"
    modified_at = "modified_at"
    score = "score"

@router.get("/", response_description="Users retrieved")
async def get_users(response: Response, order_by: UserOrderBy = UserOrderBy.followers, asc: bool = False, page: int = 1, limit: int = 10):
    users, total_pages = await mongo_client.get_users(order_by.value, asc, page-1,limit)
    if users:
        return PaginatedResponseModel(users, page, limit, total_pages)
    response.status_code = status.HTTP_204_NO_CONTENT
    return ResponseModel([], "No content")

@router.get("/{username}", response_description="Username information")
async def get_user(response: Response, username: str):
    user = await mongo_client.get_user(username)
    if user:
        return ResponseModel(user, "User returned successfully") 
    response.status_code = status.HTTP_404_NOT_FOUND
    return ResponseModel([], "User not found")


@router.get("/{username}/following", response_description="Users followed by the user")
async def get_following(response: Response, username: str, order_by: UserOrderBy = UserOrderBy.followers, asc: bool = False, page: int = 1, limit: int = 10):
    user = await mongo_client.get_user(username)
    if user:
        # get followings from neo
        followed_ids = neo_client.get_followed_users(user['_id'])
        if followed_ids:
            # get users by array of ids from mongo
            users, total_pages = await mongo_client.get_users_by_id(followed_ids, order_by.value, asc, page-1, limit)

            # return paginated response
            return PaginatedResponseModel(users, page, limit, total_pages)
        else:
            response.status_code = status.HTTP_204_NO_CONTENT
            return ResponseModel([], "No content")
    else:
        response.status_code = status.HTTP_404_NOT_FOUND
        return ResponseModel([], "User not found")

@router.get("/{username}/followed_by", response_description="Users that follow the user")
async def get_following(response : Response, username: str, order_by: UserOrderBy = UserOrderBy.followers, asc: bool = False, page: int = 1, limit: int = 10):
    user = await mongo_client.get_user(username)
    if user:
        # get followings from neo
        followed_ids = neo_client.get_followed_by_users(user['_id'])
        if followed_ids:
            # get users by array of ids from mongo
            users, total_pages = await mongo_client.get_users_by_id(followed_ids, order_by.value, asc, page-1, limit)
            # return paginated response
            return PaginatedResponseModel(users, page, limit, total_pages)
        else:
            response.status_code = status.HTTP_204_NO_CONTENT
            return ResponseModel([], "No content")
    else:
        response.status_code = status.HTTP_404_NOT_FOUND
        return ResponseModel([], "User not found")

@router.post("/{username}/follow/{other_username}", response_description="Follow another user")
async def follow(response : Response, username: str, other_username: str):
    user = await mongo_client.get_user(username) 
    other_user = await mongo_client.get_user(other_username) 
    if not user:
        response.status_code = status.HTTP_404_NOT_FOUND
        return ResponseModel([], "User {} does not exist".format(username))
    if not other_user:
        response.status_code = status.HTTP_404_NOT_FOUND
        return ResponseModel([],"User {} does not exist".format(other_username))
    if not neo_client.is_following(user['_id'], other_user['_id']):
        result = neo_client.create_following(user['_id'], other_user['_id'])
        if not result:
            response.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
            return ResponseModel([], "Could not follow")
    followers_url = f"http://{server_host}:{server_port}/users/{username}/following"
    return ResponseModel(followers_url, "Following successfully")

@router.post("/{username}/unfollow/{other_username}", response_description="Stop following another user")
async def unfollow(response : Response, username: str, other_username: str):
    user = await mongo_client.get_user(username) 
    other_user = await mongo_client.get_user(other_username) 
    if not user:
        response.status_code = status.HTTP_404_NOT_FOUND
        return ResponseModel([], "User {} does not exist".format(username))
    if not other_user:
        response.status_code = status.HTTP_404_NOT_FOUND
        return ResponseModel([],"User {} does not exist".format(other_username))
    if neo_client.is_following(user['_id'], other_user['_id']):
        result = neo_client.delete_following(user['_id'], other_user['_id'])
        if not result:
            response.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
            return ResponseModel([], "Could not unfollow")
    followers_url = f"http://{server_host}:{server_port}/users/{username}/following"
    return ResponseModel(followers_url, "Unfollowed successfully")

        


@router.get("/{username}/reviews", response_description="Users that follow the user")
async def get_reviews(response : Response, username: str, order_by: ReviewOrderBy = ReviewOrderBy.created_at, asc: bool = False, page: int = 1, limit: int = 10):
    user = await mongo_client.get_user(username)
    if user:
        # get reviews from neo
        review_ids = neo_client.get_reviews_for_user(user['_id'])
        if review_ids:
            # get reviews by array of ids from mongo
            users, total_pages = await mongo_client.get_reviews_with_repo(review_ids, order_by.value, asc, page-1, limit)
            # return paginated response
            return PaginatedResponseModel(users, page, limit, total_pages)
        response.status_code = status.HTTP_204_NO_CONTENT
        return ResponseModel([],  "No content")
    response.status_code = status.HTTP_404_NOT_FOUND
    return ResponseModel([], "User {} does not exist".format(username))


@router.put("/{username}", response_description="Edit user")
async def edit_user(response : Response, username: str, req: UpdateUserModel = Body(...)):
    req = {k:v for k, v in req.dict().items() if v is not None}
    user = await mongo_client.get_user(username)
    if user:
        updated_user = await mongo_client.update_user(user["_id"], req)
        if updated_user:
            return ResponseModel("User {} updated successfully".format(username), "User updated successfully")
        else:
            response.status_code = status.HTTP_404_NOT_FOUND
            return ResponseModel([], "There was an error updating the user data")
    else:
        response.status_code = status.HTTP_404_NOT_FOUND
        return ResponseModel([], "User not found")

@router.get("/{username}/recommended/repos", response_description="Users retrieved")
async def get_recommended_repos(response : Response, username: str, depth: int = 1, page: int = 1, limit: int = 10):
    user = await mongo_client.get_user(username)
    if user:
        recommended_ids = neo_client.get_recommended_repos(user['_id'], depth=depth+1)
    
        if recommended_ids:
            repos, total_pages = await mongo_client.get_repos_recommendations_by_id(user,recommended_ids, page-1, limit)
            return PaginatedResponseModel(repos, page, limit, total_pages)
        else:
            return {
                "message": "No recommendations found", 
                "most_starred_repos_url": f"http://{server_host}:{server_port}/repos/?order_by=stars&asc=false&page=1&limit=10"
            }
    response.status_code = status.HTTP_404_NOT_FOUND
    return ResponseModel([], "User not found")




@router.get("/{username}/recommended/users", response_description="Retrieves recommended users for specified user")
async def get_recommended_users(response: Response, username: str, depth: int = 1, page: int = 1, limit: int = 10):
    user = await mongo_client.get_user(username)
    if user:
        recommended_ids = neo_client.get_recommended_users(user['_id'], depth=depth+1)
        print("base amount of users: " + str(len(recommended_ids)))
        if recommended_ids:
            users, total_pages = await mongo_client.get_user_recommendations_by_id(user,recommended_ids, page-1, limit)
            return PaginatedResponseModel(users, page, limit, total_pages)
        else:
            return {"message": "No recommendations found", "most_followed_users_url": f"http://{server_host}:{server_port}/users/?order_by=followers&asc=false&page=1&limit=10"}
    response.status_code = status.HTTP_204_NO_CONTENT
    return ResponseModel([], "No content")
