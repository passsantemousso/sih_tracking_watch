import paho.mqtt.client as mqtt
import logging

class MQTTHandler:
    """
    Gestionnaire MQTT pour la connexion, la publication et la gestion de messages avec un broker MQTT.
    """

    def __init__(self, broker_address='localhost', port=1883, client_id=None):
        """
        Initialise le client MQTT.

        Args:
            broker_address (str): Adresse du broker MQTT.
            port (int): Port du broker MQTT.
            client_id (str): Identifiant du client MQTT (par défaut, un identifiant généré automatiquement).
        """
        self.logger = logging.getLogger(__name__)
        self.logger.info("Initialisation de MQTTHandler.")

        self.broker_address = broker_address
        self.port = port
        self.client_id = client_id or "default_client"
        self.client = mqtt.Client(client_id=self.client_id, protocol=mqtt.MQTTv5)

        # Attachement des callbacks par défaut
        self.client.on_connect = self.on_connect
        self.client.on_disconnect = self.on_disconnect
        self.client.on_publish = self.on_publish

    def on_connect(self, client, userdata, flags, rc, properties=None):
        """
        Callback appelé lors de la connexion au broker MQTT.

        Args:
            client: Instance du client MQTT.
            userdata: Données utilisateur définies (par défaut, None).
            flags: Drapeaux de connexion sous forme de dictionnaire.
            rc: Code de retour de connexion (0 pour succès).
            properties: Propriétés MQTT (uniquement pour MQTTv5).
        """
        if rc == 0:
            self.logger.info(f"Connecté au broker MQTT à {self.broker_address}:{self.port}.")
        else:
            self.logger.error(f"Échec de connexion au broker MQTT, code : {rc}.")

    def on_disconnect(self, client, userdata, rc):
        """
        Callback appelé lors de la déconnexion du broker MQTT.

        Args:
            client: Instance du client MQTT.
            userdata: Données utilisateur définies (par défaut, None).
            rc: Code de retour de déconnexion.
        """
        self.logger.info("Déconnecté du broker MQTT.")
        if rc != 0:
            self.logger.warning("Déconnexion inattendue du broker MQTT.")

    def on_publish(self, client, userdata, mid):
        """
        Callback appelé après la publication d'un message.

        Args:
            client: Instance du client MQTT.
            userdata: Données utilisateur définies (par défaut, None).
            mid: ID du message publié.
        """
        self.logger.info(f"Message publié avec ID {mid}.")

    async def mqtt_loop(self):
        """
        Démarre la boucle MQTT dans un environnement asyncio.
        """
        try:
            self.logger.info("Démarrage de la boucle MQTT.")
            self.client.loop_start()  # Boucle bloquante pour écouter les messages
        except Exception as e:
            self.logger.error(f"Erreur dans la boucle MQTT : {e}", exc_info=True)

    def connect(self):
        """
        Connecte le client au broker MQTT.
        """
        try:
            self.logger.info(f"Tentative de connexion au broker MQTT à {self.broker_address}:{self.port}.")
            self.client.connect(self.broker_address, self.port)
            self.logger.info("Connexion réussie. Boucle MQTT prête à démarrer.")
        except Exception as e:
            self.logger.error(f"Erreur lors de la connexion au broker MQTT : {e}", exc_info=True)

    def publish(self, topic, message):
        """
        Publie un message sur un topic spécifique.

        Args:
            topic (str): Le topic où publier le message.
            message (str): Le message à publier.
        """
        try:
            if self.client.is_connected():
                self.client.publish(topic, message)
                self.logger.info(f"Message publié sur le topic '{topic}' : {message}")
            else:
                self.logger.warning("Client MQTT non connecté. Publication impossible.")
        except Exception as e:
            self.logger.error(f"Erreur lors de la publication sur le topic '{topic}' : {e}", exc_info=True)

    def disconnect(self):
        """
        Déconnecte proprement le client MQTT.
        """
        try:
            self.client.loop_stop()  # Arrête la boucle MQTT
            self.client.disconnect()  # Déconnecte du broker
            self.logger.info("Déconnecté du broker MQTT.")
        except Exception as e:
            self.logger.error(f"Erreur lors de la déconnexion : {e}", exc_info=True)
