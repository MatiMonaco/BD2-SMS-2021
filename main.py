import uvicorn
from uvicorn import config
from config import config


if __name__ == "__main__":
    uvicorn.run("app.server.app:app", host=config.SERVER_URL, port=config.PORT, reload=True)
