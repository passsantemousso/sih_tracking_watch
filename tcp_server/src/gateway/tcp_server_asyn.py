import asyncio
from datetime import datetime, timezone
import logging
from ..core.config import settings


class TCPServerAsync:
    def __init__(self, mqtt_handler, packet_processor, host='0.0.0.0', port=6020, buffer_size=1024, is_debug=False):
        self.logger = logging.getLogger(__name__)
        self.logger.info("Initialisation de TCPServer")

        self.mqtt_handler = mqtt_handler
        self.packet_processor = packet_processor
        self.host = host
        self.port = port
        self.buffer_size = buffer_size
        self.server = None
        self.device_map = {}  # Dictionnaire pour associer (IP, port) à IMEI
        self.is_debug = is_debug

    @staticmethod
    def extract_imei(message):
        """Extrait l'IMEI d'un paquet AP00."""
        imei = message[6:-1]
        return imei if imei else None

    async def handle_client(self, client_reader, client_writer):
        client_address = client_writer.get_extra_info('peername')
        self.logger.info(f"Connexion établie avec {client_address}")

        imei = None

        try:
            while True:
                data = await client_reader.read(self.buffer_size)
                if not data:
                    self.logger.info(f"Connexion fermée par le client : {client_address}")
                    break

                try:
                    message = data.decode("utf-8", errors='replace').strip()
                except UnicodeDecodeError as e:
                    self.logger.error(f"Erreur d'encodage: {e}")
                    return

                # Journalisation conditionnelle pour les données reçues
                if self.is_debug:
                    self.logger.debug(f"Données reçues de {client_address}: {message}")

                # Si c'est un paquet AP00 contenant l'IMEI, on l'associe
                if message.startswith("IWAP") and "AP00" in message:
                    imei = self.extract_imei(message)

                    if imei and imei not in self.device_map:
                        self.device_map[imei] = {"last_address": client_address}
                        if self.is_debug:
                            self.logger.debug(f"IMEI {imei} associé à {client_address}")

                        # Réponse avec le paquet BP00
                        current_time = datetime.now(timezone.utc)
                        server_time = current_time.strftime("%Y%m%d%H%M%S")
                        timezone_offset = current_time.utcoffset().total_seconds() // 3600  # Décalage en heures
                        response = f"IWBP00,{server_time},{int(timezone_offset)}#"

                        if response:
                            client_writer.write(response.encode('utf-8'))
                            await client_writer.drain()
                            if self.is_debug:
                                self.logger.debug(f"Réponse envoyée à {client_address[0]} : {response}")
                    continue  # Passer au prochain paquet sans traitement

                if message.startswith(settings.IGNORED_MESSAGES):
                    continue

                if not imei:
                    self.logger.warning(f"Aucun IMEI trouvé pour {client_address}")
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
                    if self.is_debug:
                        self.logger.debug(f"Réponse envoyée à {client_address[0]} : {response}")
        except Exception as e:
            self.logger.error(f"Erreur avec {client_address}: {e}", exc_info=True)
        finally:
            self.logger.info(f"Fermeture de la connexion avec {client_address}")
            client_writer.close()
            await client_writer.wait_closed()

    async def start(self):
        try:
            self.server = await asyncio.start_server(self.handle_client, self.host, self.port)
            addr = self.server.sockets[0].getsockname()
            self.logger.info(f"Serveur TCP démarré sur {addr}")

            async with self.server:
                await self.server.serve_forever()
        except Exception as e:
            self.logger.error(f"Erreur dans le démarrage du serveur : {e}", exc_info=True)

    async def stop(self):
        if self.server:
            self.server.close()
            await self.server.wait_closed()
            self.logger.info("Serveur TCP arrêté.")
