# device_repository.py
import os
import logging
from datetime import datetime, timezone
from pymongo.errors import CollectionInvalid
from src.utils.utils import check_docker_run

check_docker_run()

class DeviceRepository:
    def __init__(self, mongo_helper, is_debug=False):
        """
        Initialise le repository avec une instance de MongoDBHelper.
        Args:
            mongo_helper (MongoDBHelper): instance déjà configurée pour se connecter à MongoDB.
            is_debug (bool): Active ou désactive les logs de débogage.
        """
        self.logger = logging.getLogger(__name__)
        self.is_debug = is_debug
        self.db = mongo_helper.db
        self.collection_name = os.getenv("MONGO_COLLECTION_DEVICE")
        self.ensure_collection_exists()
        self.devices_collection = self.db[self.collection_name]


    def ensure_collection_exists(self):
        """
        Vérifie que la collection 'devices' existe, sinon la crée.
        """
        try:
            self.db.create_collection(self.collection_name)
            self.logger.info(f"Collection {self.collection_name} créée dans MongoDB.")
        except CollectionInvalid:
            self.logger.info(f"Collection {self.collection_name} déjà existante.")
        except Exception as e:
            self.logger.error(f"Erreur lors de la vérification/création de la collection {self.collection_name} :"
                              f"{e}", exc_info=self.is_debug)

    def find_device_by_imei(self, imei):
        """
        Recherche et retourne le document associé à un IMEI.
        Args:
            imei (str): numéro IMEI de la montre.
        Returns:
            dict ou None: Document Mongo correspondant ou None s'il n'existe pas.
        """
        try:
            return self.devices_collection.find_one({"imei": imei})
        except Exception as e:
            self.logger.error(f"Erreur lors de la recherche du device pour l'IMEI {imei} : {e}", exc_info=self.is_debug)
            return None

    def save_new_device(self, imei, address):
        """
        Enregistre un nouvel enregistrement pour une montre.
        Args:
            imei (str): numéro IMEI.
            address (tuple): adresse du client (IP, port).
        """
        try:
            doc = {
                "imei": imei,
                "last_address": address,
                "created_at": datetime.now(timezone.utc)
            }
            self.devices_collection.insert_one(doc)
            if self.is_debug:
                self.logger.debug(f"Nouvelle montre insérée : {doc}")
        except Exception as e:
            self.logger.error(f"Erreur lors de l'insertion du nouveau device : {e}", exc_info=self.is_debug)

    def update_device_address(self, imei, address):
        """
        Met à jour l'adresse de connexion pour une montre existante.
        Args:
            imei (str): numéro IMEI.
            address (tuple): nouvelle adresse (IP, port).
        """
        try:
            self.devices_collection.update_one(
                {"imei": imei},
                {
                    "$set": {
                        "last_address": address,
                        "updated_at": datetime.now(timezone.utc)
                    }
                }
            )
            if self.is_debug:
                self.logger.debug(f"Mise à jour de l'adresse pour l'IMEI {imei} : {address}")
        except Exception as e:
            self.logger.error(f"Erreur lors de la mise à jour de l'adresse pour l'IMEI {imei} : {e}", exc_info=self.is_debug)

    def update_device_disconnection_time(self, imei, disconnection_time=None):
        """
        Met à jour le timestamp de déconnexion pour le device avec l'IMEI donné.
        """
        disconnection_time = disconnection_time or datetime.now(timezone.utc)
        try:
            self.devices_collection.update_one(
                {"imei": imei},
                {"$set": {"last_disconnection": disconnection_time}}
            )
        except Exception as e:
            self.logger.error(f"Erreur lors de la mise à jour du timestamp de déconnexion pour l'IMEI {imei} : {e}",
                              exc_info=True
            )