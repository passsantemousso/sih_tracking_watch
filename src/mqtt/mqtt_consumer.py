import paho.mqtt.client as mqtt
import traceback
import json

class MqttConsumer:
    """Consommateur MQTT pour traiter les messages et stocker dans MongoDB."""

    def __init__(self, mongodb_helper, packet_processor, broker_address='localhost', port=1883, topic='health_data_topic'):
        """
        Initialise le consommateur MQTT.

        Args:
            broker_address (str): Adresse du broker MQTT.
            port (int): Port du broker MQTT.
            topic (str): Topic à écouter.
            packet_processor (PacketProcessor): Instance de la classe PacketProcessor.
            mongodb_helper (MongoDBHelper): Instance de la classe MongoDBHelper.
        """
        self.broker_address = broker_address
        self.port = port
        self.topic = topic
        self.packet_processor = packet_processor
        self.mongodb_helper = mongodb_helper
        self.client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2, protocol=mqtt.MQTTv5)

    def on_connect(self, client, userdata, flags, rc, properties=None):
        """Callback appelé lors de la connexion au broker MQTT."""
        """
            Callback appelé lors de la connexion au broker MQTT.

            Args:
                client: Instance du client MQTT.
                userdata: Données définies par l'utilisateur (optionnelles).
                flags: Drapeaux de connexion sous forme de dictionnaire.
                rc: Code de retour de connexion (0 pour succès).
                properties: Propriétés MQTT (uniquement pour MQTTv5).
        """

        if rc == 0:
            print("Connecté au broker MQTT.")
            self.client.subscribe(self.topic)
        else:
            print(f"Échec de connexion avec le code {rc}.")

    def on_message(self, client, userdata, msg):
        """Callback appelé lors de la réception d'un message."""
        try:
            # Décodage du message
            payload_data = msg.payload.decode("utf-8").strip()
            # Remplacement des guillemets simples par des guillemets doubles
            if payload_data.startswith("{") and "'" in payload_data:
                payload_data = payload_data.replace("'", '"')

            message = json.loads(payload_data)
            print(f"Message reçu sur le topic {msg.topic}: {message}")

            raw_data = message["raw_data"]

            # Identification et traitement du paquet
            packet_type = raw_data[2:6]  # Ex: AP00, AP01, etc.
            processor_method = getattr(self.packet_processor, f"extract_{packet_type.lower()}_data", None)
            print("La méthode est :", processor_method)

            if processor_method:
                # Appel de la méthode de traitement
                extracted_data = {
                    "imei": message["imei"],
                    "model": "VL08",
                    "command_type": message["command_type"],
                    "data": processor_method(raw_data),
                    "created_at": message['created_at'],
                    "updated_at": message['updated_at']
                }

                print(f"Données extraites : {json.dumps(extracted_data, indent=2)}")

                # Stockage dans MongoDB
                collection_name = packet_type.lower()  # Ex : "ap00"
                self.mongodb_helper.insert_data('health_data', extracted_data)
            else:
                print(f"Aucun processeur trouvé pour le type de paquet : {packet_type}")

        except Exception as e:
            print(f"Erreur lors du traitement du message MQTT : {e}")
            traceback.print_exc()

    def start(self):
        """Démarre le consommateur MQTT."""
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message

        print("Connexion au broker MQTT...")
        self.client.connect(self.broker_address, self.port)
        self.client.loop_start()

    async def stop(self):
        if self.client:
            self.client.loop_stop()
            self.client.disconnect()
            print("Consommateur MQTT arrêté.")