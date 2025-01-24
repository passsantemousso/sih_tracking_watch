import os
from pydantic_settings import BaseSettings
from src.utils.utils import check_docker_run

check_docker_run()

class Settings(BaseSettings):
    MONGO_URI: str = os.getenv("MONGO_URI")
    MONGO_DB_NAME: str = os.getenv("MONGO_DB_NAME")
    MONGO_DB_COLLECTION: str = os.getenv("MONGO_COLLECTION")

settings = Settings()