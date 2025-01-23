import os
from pydantic_settings import BaseSettings
from dotenv import load_dotenv

load_dotenv()

class Settings(BaseSettings):
    MONGO_URI: str = os.getenv("MONGO_URI", "mongodb://localhost:27017")
    MONGO_DB_NAME: str = os.getenv("MONGO_DB_NAME", "health_watch_data_db")
    MONGO_DB_COLLECTION: str = os.getenv("MONGO_COLLECTION", "health_data")

settings = Settings()