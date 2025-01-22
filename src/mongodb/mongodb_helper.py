from pymongo import MongoClient
from dotenv import load_dotenv
import os
import logging

load_dotenv()

class MongoDBHelper:
    def __init__(self, is_debug=False):
        """
        Initialise l'helper MongoDB avec des paramètres environnementaux.
        Args:
            is_debug (bool): Active ou désactive les journaux de débogage.
        """
        self.logger = logging.getLogger(__name__)
        self.is_debug = is_debug

        self.uri = os.getenv("MONGO_URI")
        self.db_name = os.getenv("MONGO_DB")
        self.collection_name = os.getenv("MONGO_COLLECTION")

        if not self.uri or not self.db_name or not self.collection_name:
            self.logger.error(
                "Les variables d'environnement MONGO_URI, MONGO_DB ou MONGO_COLLECTION sont manquantes ou invalides."
            )
            raise ValueError(
                "Les variables d'environnement MONGO_URI, MONGO_DB ou MONGO_COLLECTION sont manquantes ou invalides."
            )

        self.client = MongoClient(self.uri)
        self.db = self.client[self.db_name]

    def test_connection(self):
        """Test la connexion à MongoDB."""
        try:
            # Test de la connexion en envoyant une commande 'ping'
            self.client.admin.command('ping')
            self.logger.info("Connexion à MongoDB réussie.")
        except Exception as e:
            self.logger.error(f"Impossible de se connecter à MongoDB : {e}", exc_info=self.is_debug)
            raise ConnectionError(f"Impossible de se connecter à MongoDB : {e}")

    def insert_data(self, collection_name, data):
        """Insère les données dans la collection MongoDB de manière synchrone."""
        try:
            # Insertion synchrone des données
            self.db[collection_name].insert_one(data)
            self.logger.info(f"Données insérées dans la collection '{collection_name}'.")
            if self.is_debug:
                self.logger.debug(f"Données insérées : {data}")
        except Exception as e:
            self.logger.error(f"Erreur lors de l'insertion dans MongoDB : {e}", exc_info=self.is_debug)

    def ensure_collection_exists(self):
        """Vérifie si la collection existe et la crée si nécessaire."""
        try:
            collections = self.db.list_collection_names()
            if self.collection_name not in collections:
                self.db.create_collection(self.collection_name)
                self.logger.info(f"Collection '{self.collection_name}' créée.")
            else:
                self.logger.info(f"Collection '{self.collection_name}' déjà existante.")
        except Exception as e:
            self.logger.error(f"Erreur lors de la vérification/création de la collection : {e}", exc_info=self.is_debug)
