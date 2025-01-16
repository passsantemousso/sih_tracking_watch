from kafka import KafkaConsumer
import json

def main():
    # Créer un consommateur Kafka
    consumer = KafkaConsumer(
        'health_data',  # Nom du topic
        bootstrap_servers=['localhost:9092'],  # Adresse de votre broker Kafka
        group_id='health_data_group',  # Groupe de consommateur
        auto_offset_reset='earliest',  # Lire à partir du début du topic
        enable_auto_commit=True,
        value_deserializer=lambda x: json.loads(x.decode('utf-8'))  # Désérialiser les messages JSON
    )

    print("Consommateur Kafka démarré...")

    try:
        for message in consumer:
            # Message reçu
            print(f"Message reçu : {message.value}")

            # Exemple : traiter les données
            process_data(message.value)
    except KeyboardInterrupt:
        print("Consommateur arrêté.")
    finally:
        consumer.close()

def process_data(data):
    """
    Traitement des données reçues.
    """
    # Ajoutez ici le code pour traiter et sauvegarder les données
    print(f"Traitement des données : {data}")

if __name__ == "__main__":
    main()
