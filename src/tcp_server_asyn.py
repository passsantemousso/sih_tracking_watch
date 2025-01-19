import asyncio
import datetime
from datetime import timezone
from paquets.packet_processor import PacketProcessor
from kafka_custom.producer.kafka_producer import KafkaProducerWrapper

class TCPServer:
    def __init__(self, host='0.0.0.0', port=6020, kafka_topic='health_data', kafka_brokers=None):
        self.TCP_IP = host
        self.TCP_PORT = port
        self.BUFFER_SIZE = 1024
        self.processor = PacketProcessor()
        self.kafka_producer = KafkaProducerWrapper(
            brokers=kafka_brokers or ['127.0.0.1:9092'],
            topic=kafka_topic
        )

    async def handle_client(self, client_reader, client_writer):
        """Gère la communication avec un client."""
        client_address = client_writer.get_extra_info('peername')
        print(f"Connexion établie avec {client_address}")

        try:
            while True:
                # Recevoir les données du client
                data = await client_reader.read(self.BUFFER_SIZE)
                if not data:
                    print(f"Connexion fermée par le client : {client_address}")
                    break

                message = data.decode('utf-8').strip()
                print(f"Données reçues de {client_address}: {message}")
                await self.process_and_send(message)

                # Réponse du serveur à la montre
                response = self.processor.process_message_response(message)
                if response:
                    client_writer.write(response.encode('utf-8'))
                    await client_writer.drain()  # S'assurer que la réponse est envoyée
                    print(f"Réponse envoyée à {client_address}: {response}")
        except Exception as e:
            print(f"Erreur avec {client_address}: {e}")
        finally:
            print(f"Fermeture de la connexion avec {client_address}")
            client_writer.close()
            await client_writer.wait_closed()

    async def process_and_send(self, data):
        """
        Traite les données reçues et les envoie au producteur Kafka.
        """
        # Traitement des données
        processed_data = {
            "raw_data": data,
            "processed_at": datetime.datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
        }
        await self.kafka_producer.send(processed_data)

    async def start(self):
        """Démarre le serveur TCP."""
        server = await asyncio.start_server(
            self.handle_client,
            self.TCP_IP,
            self.TCP_PORT
        )

        addr = server.sockets[0].getsockname()
        print(f"Serveur TCP démarré sur {addr}")

        try:
            await server.serve_forever()
        except KeyboardInterrupt:
            print("\nArrêt du serveur...")
        finally:
            server.close()
            await server.wait_closed()
            print("Serveur arrêté.")

if __name__ == "__main__":
    # Configuration du serveur
    HOST = '0.0.0.0'
    PORT = 6015
    MAX_SIZE = 10 * 1024 * 1024  # 10 Mo

    # IMEI
    IMEI = "861265062672529"

    server = TCPServer()
    asyncio.run(server.start())
