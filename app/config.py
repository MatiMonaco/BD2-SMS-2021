import os
from dotenv import load_dotenv

load_dotenv()  # take environment variables from .env.


config = {
    'MONGO_DETAILS': os.environ.get('MONGO_DETAILS'),
    'NEO4J_DETAILS': os.environ.get('NEO4J_DETAILS'),
    'SERVER_URL': os.environ.get('SERVER_URL'),
    'PORT': os.environ.get('PORT'),
    'GITHUB_API_TOKEN': os.environ.get('GITHUB_API_TOKEN'),
}