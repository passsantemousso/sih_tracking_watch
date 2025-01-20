import paho.mqtt.client as mqtt


class MQTTHandler:
    def __init__(self, broker_address='localhost', port=1883, client_id=None):
        """
        Initialise le client MQTT.

        Args:
            broker_address (str): Adresse du broker MQTT.
            port (int): Port du broker MQTT.
            client_id (str): Identifiant du client MQTT.
        """
        self.broker_address = broker_address
        self.port = port
        self.client_id = client_id or "default_client"
        self.client = mqtt.Client(client_id=self.client_id, protocol=mqtt.MQTTv5)

    def connect(self):
        """
        Connecte le client au broker MQTT et démarre la boucle.
        """
        try:
            self.client.connect(self.broker_address, self.port)
            self.client.loop_start()
            print(f"Connecté au broker MQTT à {self.broker_address}:{self.port}")
        except Exception as e:
            print(f"Erreur lors de la connexion au broker MQTT : {e}")

    def publish(self, topic, message):
        """
        Publie un message sur un topic spécifique.

        Args:
            topic (str): Le topic où publier le message.
            message (str): Le message à publier.
        """
        if self.client.is_connected():
            self.client.publish(topic, message)
            print(f"Message publié sur le topic '{topic}' : {message}")
        else:
            print("Client MQTT non connecté. Impossible de publier le message.")

    def disconnect(self):
        """
        Déconnecte proprement le client MQTT.
        """
        try:
            self.client.loop_stop()
            self.client.disconnect()
            print("Déconnecté du broker MQTT.")
        except Exception as e:
            print(f"Erreur lors de la déconnexion : {e}")
