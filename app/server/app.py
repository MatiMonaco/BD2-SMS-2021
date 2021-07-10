from fastapi import FastAPI
from server.routes.repos import router as ReposRouter
from server.routes.users import router as UsersRouter
app = FastAPI()


app.include_router(ReposRouter, tags=["Repos"], prefix="/repos")
#app.include_router(UsersRouter, tags=["Users"], prefix="/repos")
@app.get("/", tags=["Root"])
async def root():
    return {"message": "Hello World"}
