import os
from pydantic_settings import BaseSettings
from dotenv import load_dotenv

load_dotenv()

class Settings(BaseSettings):
    # Configuration générale
    TCP_HOST: str = os.getenv("TCP_HOST", "0.0.0.0")
    TCP_PORT: str = int(os.getenv("TCP_PORT", 6020))

    # Kafka
    KAFKA_BROKER: str = os.getenv("KAFKA_BROKER", "kafka_custom:9092")
    KAFKA_TOPIC: str = os.getenv("KAFKA_TOPIC", "tracking_watch_data")

    # MongoDB
    MONGO_URI: str = os.getenv("MONGO_URI")
    MONGO_DB_NAME: str = os.getenv("MONGO_DB_NAME", "tracking_watch")
    MONGO_DB_COLLECTION: str = os.getenv("MONGO_COLLECTION", "health_data")

    MQTT_BROKER: str = os.getenv("MQTT_BROKER", "localhost")
    MQTT_TOPIC: str = os.getenv("MQTT_TOPIC", "tracking_watch_data")

    IGNORED_MESSAGES: tuple = ("IWAP02", "IWAP03", "IWAP07", "IWAPHT", "IWAP50", "IWAP40")

settings = Settings()


