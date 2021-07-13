from fastapi import FastAPI
from server.routes.repos import router as ReposRouter
from server.routes.users import router as UsersRouter
from pydantic import BaseModel, Field

class UsernameSchema(BaseModel):
    username: str = Field(...)


app = FastAPI()


app.include_router(ReposRouter, tags=["Repos"], prefix="/repos")
app.include_router(UsersRouter, tags=["Users"], prefix="/users")
@app.get("/", tags=["Root"])
async def root():
    return {"message": "Hello World"}

@app.get("/login", tags=["User login"])
async def login(username: UsernameSchema):
    return {"message": "Hello World"}