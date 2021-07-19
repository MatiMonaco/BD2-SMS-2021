import os
from dotenv import load_dotenv

load_dotenv()  # take environment variables from .env.


config = {
    
    "MONGO_DETAILS": os.environ.get('MONGO_DETAILS'),
    "NEO4J_DETAILS": os.environ.get('NEO4J_DETAILS'),
    "NEO4J_USER": os.environ.get('NEO4J_USER'),
    "NEO4J_PASS": os.environ.get('NEO4J_PASS'),
    "SERVER_HOST": os.environ.get('SERVER_HOST'),
    "PORT": os.environ.get('PORT'),
    "GITHUB_API_TOKEN": os.environ.get('GITHUB_API_TOKEN'),
}