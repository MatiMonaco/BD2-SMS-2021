from fastapi import APIRouter, Body
from fastapi.encoders import jsonable_encoder
from server.models.status_code_enum import StatusCodeEnum


from server.models.response_model_types import (
    ErrorResponseModel,
    ResponseModel,
    # NewsSchema,
)

router = APIRouter()


@router.get("/{username}/recommended/repos", response_description="Users retrieved")
async def get_recommended_repos():
    news = await retrieve_news()
    if news:
        return ResponseModel(news, StatusCodeEnum.OK.value, "Successfully retrieved all news")
    return ResponseModel(news, StatusCodeEnum.OK.value, "Empty list returned")


@router.get("/{username}/recommended/users", response_description="Users retrieved")
async def get_recommended_users():
   # news = await retrieve_news()
    if news:
        return ResponseModel(news, StatusCodeEnum.OK.value, "Successfully retrieved all news")
    return ResponseModel(news, StatusCodeEnum.OK.value, "Empty list returned")
