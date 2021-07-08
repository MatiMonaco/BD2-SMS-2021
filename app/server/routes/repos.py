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


@router.get("/{username}/{reponame}/review", response_description="Repos retrieved")
async def get_repo_reviews():
    news = await retrieve_news()
    if news:
        return ResponseModel(news, "Successfully retrieved all news")
    return ResponseModel(news, "Empty list returned")



