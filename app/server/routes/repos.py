from fastapi import APIRouter, Body
from fastapi.encoders import jsonable_encoder
from app.server.database import mongo_client, neo_client



from app.server.models.news import (
    ErrorResponseModel,
    ResponseModel,
    NewsSchema,
)

router = APIRouter()
@router.get("/", response_description="Repos retrieved")
async def get_repos():
    repos = await mongo_client.get_repos({})
    if repos:
        return ResponseModel(repos, "Successfully retrieved all repos")
    return ResponseModel(repos, "Empty list returned")

@router.get("/{username}/{reponame}/review", response_description="Repos retrieved")
async def get_repo_reviews():
    news = await retrieve_news()
    if news:
        return ResponseModel(news, "Successfully retrieved all news")
    return ResponseModel(news, "Empty list returned")



