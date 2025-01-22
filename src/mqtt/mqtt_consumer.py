import paho.mqtt.client as mqtt
import json
import logging
import traceback

class MqttConsumer:
    """Consommateur MQTT pour traiter les messages et stocker dans MongoDB."""

    def __init__(self, mongodb_helper, packet_processor, broker_address='localhost', port=1883, topic='health_data_topic', is_debug=False):
        self.logger = logging.getLogger(__name__)
        self.logger.info("Initialisation de MqttConsumer")

        self.broker_address = broker_address
        self.port = port
        self.topic = topic
        self.packet_processor = packet_processor
        self.mongodb_helper = mongodb_helper
        self.client = mqtt.Client()
        self.is_debug = is_debug

    def on_connect(self, client, userdata, flags, rc, properties=None):
        """Callback appelé lors de la connexion au broker MQTT."""
        if rc == 0:
            self.logger.info("Connecté au broker MQTT.")
            self.client.subscribe(self.topic)
        else:
            self.logger.error(f"Échec de connexion avec le code {rc}.")

    def on_message(self, client, userdata, msg):
        """Callback appelé lors de la réception d'un message."""
        try:
            # Traitement synchrone du message
            self.handle_message(msg)
        except Exception as e:
            self.logger.error(f"Erreur lors du traitement du message MQTT: {e}")
            self.logger.debug(traceback.format_exc())

    def handle_message(self, msg):
        """Traite un message reçu de manière synchrone."""
        try:
            # Décodage du message
            payload_data = msg.payload.decode("utf-8").strip()
            if payload_data.startswith("{") and "'" in payload_data:
                payload_data = payload_data.replace("'", '"')

            message = json.loads(payload_data)
            if self.is_debug:
                self.logger.debug(f"Message reçu sur le topic {msg.topic}: {message}")

            raw_data = message["raw_data"]

            # Identification et traitement du paquet
            packet_type = raw_data[2:6]  # Ex: AP00, AP01, etc.
            processor_method = getattr(self.packet_processor, f"extract_{packet_type.lower()}_data", None)

            if self.is_debug:
                self.logger.debug(f"Processeur pour {packet_type}: {processor_method}")

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

                if self.is_debug:
                    self.logger.info(f"Données extraites: {json.dumps(extracted_data, indent=2)}")

                # Stockage dans MongoDB de manière synchrone
                self.mongodb_helper.insert_data('health_data', extracted_data)
            else:
                self.logger.warning(f"Aucun processeur trouvé pour le type de paquet : {packet_type}")

        except Exception as e:
            self.logger.error(f"Erreur lors du traitement du message MQTT: {e}")
            self.logger.debug(traceback.format_exc())

    def start(self):
        """Démarre le consommateur MQTT."""
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message

        self.logger.info("Connexion au broker MQTT...")
        self.client.connect(self.broker_address, self.port)

        # Démarrer la boucle MQTT de manière synchrone
        self.client.loop_start()

    def stop(self):
        """Arrête le consommateur MQTT proprement."""
        if self.client:
            self.logger.info("Déconnexion du broker MQTT...")
            self.client.disconnect()
            self.client.loop_stop()
            self.logger.info("Consommateur MQTT arrêté.")
