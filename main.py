import uvicorn

from app.config import config


print(config)

if __name__ == "__main__":
    uvicorn.run("app.server.app:app", host=config['SERVER_HOST'], port=int(config['PORT']), reload=True)
