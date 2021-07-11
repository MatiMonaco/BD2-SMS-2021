import uvicorn
from uvicorn import config

import json
with open("app/config.json") as file:
    config = json.load(file)
    server_url = config["server_url"]
    server_port = config["server_port"]

if __name__ == "__main__":
    uvicorn.run("server.app:app", host=server_url, port=server_port, reload=True)
