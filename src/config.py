import os

# Configuration générale
TCP_HOST = os.getenv("TCP_HOST", "0.0.0.0")
TCP_PORT = int(os.getenv("TCP_PORT", 6020))

# Kafka
KAFKA_BROKER = os.getenv("KAFKA_BROKER", "kafka_custom:9092")
KAFKA_TOPIC = os.getenv("KAFKA_TOPIC", "tracking_watch_data")

# MongoDB
MONGO_URI = os.getenv("MONGO_URI", "mongodb://mongo:27017")
MONGO_DB = os.getenv("MONGO_DB", "tracking_watch")
MONGO_COLLECTION = os.getenv("MONGO_COLLECTION", "health_data")
