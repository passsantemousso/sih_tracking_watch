from pymongo import MongoClient
from dotenv import load_dotenv
import os

load_dotenv()

class MongoDBHelper:
    def __init__(self):
        # Charger les variables depuis .env
        self.uri = os.getenv("MONGO_URI")
        self.db_name = os.getenv("MONGO_DB")
        self.collection_name = os.getenv("MONGO_COLLECTION")

        # Vérification des variables chargées
        if not self.uri or not self.db_name or not self.collection_name:
            raise ValueError(
                "Les variables d'environnement MONGO_URI, MONGO_DB ou MONGO_COLLECTION sont manquantes ou invalides.")

        self.client = MongoClient(self.uri)
        self.db = self.client[self.db_name]
        self.collection = self.db[self.collection_name]

    def test_connection(self):
        """Test la connexion à MongoDB."""
        try:
            self.client.admin.command('ping')
            print("Connexion à MongoDB réussie.")
        except Exception as e:
            raise ConnectionError(f"Impossible de se connecter à MongoDB : {e}")

    def insert_data(self, collection_name, data):
        """Insère les données dans la collection MongoDB."""
        try:
            self.db[collection_name].insert_one(data)
            print(f"Données insérées dans la collection '{collection_name}'.")
        except Exception as e:
            print(f"Erreur lors de l'insertion dans MongoDB : {e}")

    def ensure_collection_exists(self):
        """Vérifie si la collection existe et la crée si nécessaire."""
        try:
            if self.collection_name not in self.db.list_collection_names():
                self.db.create_collection(self.collection_name)
                print(f"Collection '{self.collection_name}' créée.")
            else:
                print(f"Collection '{self.collection_name}' déjà existante.")
        except Exception as e:
            print(f"Erreur lors de la vérification/création de la collection : {e}")
