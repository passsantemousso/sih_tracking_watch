import asyncio
from datetime import datetime, timezone, timedelta
import re


class TCPServer:
    def __init__(self, mqtt_handler, packet_processor, host='0.0.0.0', port=6020, buffer_size=1024):
        self.mqtt_handler = mqtt_handler
        self.packet_processor = packet_processor
        self.host = host
        self.port = port
        self.buffer_size = buffer_size
        self.server = None
        self.device_map = {}  # Dictionnaire pour associer (IP, port) à IMEI

    @staticmethod
    def extract_imei(message):
        """Extrait l'IMEI d'un paquet AP00."""
        imei = message[6:-1]
        return imei if imei else None

    async def handle_client(self, client_reader, client_writer):
        client_address = client_writer.get_extra_info('peername')
        print(f"Connexion établie avec {client_address}")

        imei = None

        try:
            while True:
                data = await client_reader.read(self.buffer_size)
                if not data:
                    print(f"Connexion fermée par le client : {client_address}")
                    break

                message = data.decode('utf-8').strip()
                print(f"Données reçues de {client_address}: {message}")

                # Si c'est un paquet AP00 contenant l'IMEI, on l'associe
                if message.startswith("IWAP") and "AP00" in message:
                    imei = self.extract_imei(message)

                    if imei not in self.device_map:
                        self.device_map[imei] = {"last_address": client_address}
                        print(f"IMEI {imei} associé à {client_address}")

                        # Réponse avec le paquet BP00
                        current_time = datetime.now(timezone.utc)
                        server_time = current_time.strftime("%Y%m%d%H%M%S")
                        timezone_offset = current_time.utcoffset().total_seconds() // 3600  # Décalage en heures
                        response = f"IWBP00,{server_time},{int(timezone_offset)}#"

                        if response:
                            client_writer.write(response.encode('utf-8'))
                            await client_writer.drain()
                            print(f"Réponse envoyée à {client_address[0]} : {response}")
                    continue  # Passer au prochain paquet sans traitement

                if not imei:
                    print(f"Aucun IMEI trouvé pour {client_address}")
                    break


                # Traitement des données
                processed_data = self.packet_processor.process_raw_mqtt(message)
                processed_data['imei'] = imei  # Ajouter l'IMEI aux données

                if processed_data is not None:
                    # Publier sur MQTT via MQTTHandler
                    self.mqtt_handler.publish("health_data_topic", str(processed_data))

                # Réponse au client TCP
                response = self.packet_processor.process_message_response(message)
                if response:
                    client_writer.write(response.encode('utf-8'))
                    await client_writer.drain()
                    print(f"Réponse envoyée à {client_address[0]} : {response}")
        except Exception as e:
            print(f"Erreur avec {client_address}: {e}")
        finally:
            print(f"Fermeture de la connexion avec {client_address}")
            client_writer.close()
            await client_writer.wait_closed()

    async def start(self):
        self.server = await asyncio.start_server(self.handle_client, self.host, self.port)
        addr = self.server.sockets[0].getsockname()
        print(f"Serveur TCP démarré sur {addr}")

        async with self.server:
            await self.server.serve_forever()

    async def stop(self):
        if self.server:
            self.server.close()
            await self.server.wait_closed()
            print("Serveur TCP arrêté.")
