from kafka import KafkaProducer
import json

class KafkaProducerWrapper:
    def __init__(self, brokers, topic):
        """
        Initialise le producteur Kafka.
        :param brokers: Liste des brokers Kafka (ex: ['localhost:9092'])
        :param topic: Nom du topic Kafka
        """
        self.topic = topic
        self.producer = KafkaProducer(
            bootstrap_servers=brokers,
            value_serializer=lambda v: json.dumps(v).encode('utf-8')
        )

    def send(self, data):
        """
        Envoie des données au topic Kafka.
        :param data: Dictionnaire ou JSON à envoyer
        """
        try:
            print(f"Envoi des données à Kafka : {data}")
            self.producer.send(self.topic, data)
            self.producer.flush()
        except Exception as e:
            print(f"Erreur lors de l'envoi à Kafka : {e}")
