from fastapi import FastAPI
from app.server.routes.news import router as NewsRouter
from app.server.routes.repos import router as ReposRouter
from app.server.routes.users import router as UsersRouter
app = FastAPI()

app.include_router(NewsRouter, tags=["News"], prefix="/news")
app.include_router(ReposRouter, tags=["Repos"], prefix="/users")
app.include_router(UsersRouter, tags=["Users"], prefix="/repos")
@app.get("/", tags=["Root"])
async def root():
    return {"message": "Hello World"}
