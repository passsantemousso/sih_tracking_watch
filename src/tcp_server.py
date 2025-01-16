import socket
import threading
from paquets.packet_processor import PacketProcessor
from kafka_custom.producer.kafka_producer import KafkaProducerWrapper

class TCPServer:
    def __init__(self, host='0.0.0.0', port=6020, kafka_topic='health_data', kafka_brokers=None):
        self.TCP_IP = host
        self.TCP_PORT = port
        self.server_socket = None
        self.BUFFER_SIZE = 1024
        self.processor = PacketProcessor()
        self.kafka_producer = KafkaProducerWrapper(
            brokers=kafka_brokers or ['localhost:9092'],
            topic=kafka_topic
        )

    def start(self):
        """Démarre le serveur TCP."""
        # Création et configuration du socket
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            # Utilisation de SO_REUSEPORT si SO_REUSEADDR n'est pas disponible
            self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)
        except AttributeError:
            print("SO_REUSEPORT n'est pas disponible, passage sans option de réutilisation du port.")

        self.server_socket.bind((self.TCP_IP, self.TCP_PORT))

        print(f"Serveur TCP démarré sur {self.TCP_IP}:{self.TCP_PORT}...")

        try:
            while True:
                # Accepter une nouvelle connexion
                self.server_socket.listen()
                client_socket, client_address = self.server_socket.accept()
                print(f"Connexion établie avec {client_address[0]}:{client_address[1]}")

                # Gérer la connexion dans un thread séparé
                client_thread = threading.Thread(target=self.handle_client, args=(client_socket, client_address))
                client_thread.start()
        except KeyboardInterrupt:
            print("\nArrêt du serveur...")
        finally:
            self.stop()

    def handle_client(self, client_socket, client_address):
        """Gère la communication avec un client."""
        try:
            while True:
                # Recevoir les données du client
                data = client_socket.recv(self.BUFFER_SIZE)
                if not data:
                    print(f"Connexion fermée par le client : {client_address[0]}")
                    break

                message = data.decode('utf-8').strip()
                print(f"Données reçues de {client_address[0]} : {message}")
                self.process_and_send(message)

                # Réponse du serveur à la montre
                response = self.processor.process_message_response(message)
                if response:
                    client_socket.sendall(response.encode('utf-8'))
                    print(f"Réponse envoyée à {client_address[0]} : {response}")
        except Exception as e:
            print(f"Erreur avec {client_address[0]}: {e}")
        finally:
            client_socket.close()

    def process_and_send(self, data):
        """
        Traite les données reçues et les envoie au producteur Kafka.
        """
        # Traitement des données
        processed_data = {
            "raw_data": data,
            "processed_at": "2025-01-15T12:00:00"  #  Métadonnée ajoutée
        }
        self.kafka_producer.send(processed_data)

    def stop(self):
        """Arrête le serveur TCP et libère les ressources."""
        if self.server_socket:
            self.server_socket.close()
            print("Serveur arrêté.")


if __name__ == "__main__":
    # Configuration du serveur
    HOST = '0.0.0.0'  # Écoute sur toutes les interfaces réseau
    PORT = 6015  # Port défini pour le protocole
    MAX_SIZE = 10 * 1024 * 1024  # 10 Mo

    # IMEI
    IMEI = "861265062672529"

    # Créer une instance du serveur et démarrer
    server = TCPServer()
    server.start()


