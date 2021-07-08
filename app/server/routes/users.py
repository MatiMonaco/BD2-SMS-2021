from fastapi import APIRouter, Body
from fastapi.encoders import jsonable_encoder

from app.server.database import (
    retrieve_news,
)
from app.server.models.news import (
    ErrorResponseModel,
    ResponseModel,
    NewsSchema,
)

router = APIRouter()


@router.get("/{username}/recommended/repos", response_description="Users retrieved")
async def get_recommended_repos():
    news = await retrieve_news()
    if news:
        return ResponseModel(news, "Successfully retrieved all news")
    return ResponseModel(news, "Empty list returned")


@router.get("/{username}/recommended/users", response_description="Users retrieved")
async def get_recommended_users():
    news = await retrieve_news()
    if news:
        return ResponseModel(news, "Successfully retrieved all news")
    return ResponseModel(news, "Empty list returned")
