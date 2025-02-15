import asyncio
from datetime import datetime, timezone, timedelta
import logging

from ..core.config import settings

INACTIVITY_TIMEOUT = 300


class TCPServerAsync:
    def __init__(self, mqtt_handler, packet_processor, device_repository,
                 watch_command_service, host='0.0.0.0',
                 port=6020, buffer_size=1024, is_debug=True):

        self.logger = logging.getLogger(__name__)
        self.logger.info("Initialisation de TCPServer")

        self.mqtt_handler = mqtt_handler
        self.packet_processor = packet_processor
        self.device_repository = device_repository
        self.command_service = watch_command_service
        self.host = host
        self.port = port
        self.buffer_size = buffer_size
        self.server = None
        self.is_debug = is_debug

    @staticmethod
    def extract_imei(message):
        """Extrait l'IMEI d'un paquet AP00."""
        imei = message[6:-1]
        return imei if imei else None

    @staticmethod
    def to_unicode_hex(text: str) -> str:
        """
        Convertit un texte en une chaîne unicode hex format
        """
        return "".join(f"{ord(c):04x}" for c in text)

    @staticmethod
    def generate_journal_no_datetime() -> str:
        return datetime.now().strftime("%Y%m%d%H%M%S")

    async def handle_client(self, client_reader, client_writer):
        client_address = client_writer.get_extra_info('peername')
        self.logger.info(f"Connexion établie avec {client_address}")

        imei = None
        current_time = datetime.now(timezone.utc)

        try:
            while True:
                is_first_connection = False
                try:
                    # Lecture avec timeout d'inactivité
                    data = await asyncio.wait_for(
                        client_reader.read(self.buffer_size),
                        timeout=INACTIVITY_TIMEOUT
                    )
                except asyncio.TimeoutError:
                    self.logger.warning(f"Inactivité prolongée : fermeture de la connexion avec {client_address}")
                    break

                if not data:
                    # Fermeture du flux par le client
                    self.logger.info(f"Connexion fermée par le client : {client_address}")
                    break

                try:
                    message = data.decode("utf-8", errors='replace').strip()
                    if not message.startswith("IW"):
                        self.logger.info(f"Paquet non reconnu : {message}")
                        break
                except UnicodeDecodeError as e:
                    self.logger.error(f"Erreur d'encodage: {e}")
                    break  # Fermer la connexion si l'encodage échoue


                # Journalisation conditionnelle pour les données reçues
                if self.is_debug:
                    self.logger.debug(f"Données reçues de {client_address}: {message}")


                # Si c'est un paquet AP00 contenant l'IMEI, on l'associe
                if message.startswith("IWAP") and "AP00" in message:
                    imei = self.extract_imei(message)

                    if imei:
                        device = self.device_repository.find_device_by_imei(imei)
                        if device is None:
                            # Première connexion, insertion en base
                            self.device_repository.save_new_device(imei, client_address)
                            is_first_connection = True
                            self.logger.debug(f"IMEI {imei} inséré pour l'adresse {client_address}")

                            if self.is_debug:
                                self.logger.debug(f"IMEI {imei} inséré pour l'adresse {client_address}")
                        else:
                            # Si le champ 'last_disconnection' existe, vérifier le délai
                            if "last_disconnection" in device:
                                last_disconnection = device["last_disconnection"]
                                # last_disconnection doit être converti en datetime si nécessaire
                                if current_time - last_disconnection > timedelta(hours=1):
                                    # Le délai dépasse 1h, on envoie le paquet de notification
                                    text_unicode = self.to_unicode_hex("Hello Watch PSM!")
                                    command_str = self.command_service.send_text_message(
                                        imei=imei,
                                        text_unicode=text_unicode
                                    )
                                    self.logger.info(
                                        f"Envoi du paquet spécial à {imei} car déconnexion > 1h : {command_str}")
                                    client_writer.write(command_str.encode('utf-8'))
                                    await client_writer.drain()

                            # Mise à jour de l'adresse si nécessaire
                            self.device_repository.update_device_address(imei, client_address)

                        # Réponse avec le paquet BP00
                        server_time = current_time.strftime("%Y%m%d%H%M%S")
                        timezone_offset = current_time.utcoffset().total_seconds() // 3600  # Décalage en heures
                        response = f"IWBP00,{server_time},{int(timezone_offset)}#"

                        if response:
                            client_writer.write(response.encode('utf-8'))
                            await client_writer.drain()

                            if self.is_debug:
                                self.logger.debug(f"Réponse envoyée à {client_address[0]} : {response}")

                    if is_first_connection:
                        # Convertissez votre texte en UNICODE hex selon la notice si nécessaire
                        text_unicode = "Hello Watch PSM!"
                        # (Il s'agit de "hello watch!" en Unicode hex)

                        command_str = self.command_service.send_text_message(
                            imei=imei,
                            text_unicode=text_unicode
                        )
                        self.logger.info(f"Envoi d'un message texte à {imei}: {command_str}")

                        # Écrire la commande sur la socket
                        client_writer.write(command_str.encode('utf-8'))
                        await client_writer.drain()

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
            try:
                client_writer.close()
                await client_writer.wait_closed()
            except Exception as e:
                self.logger.error(f"Erreur lors de la fermeture de la connexion avec {client_address}: {e}",
                                  exc_info=True)
            # Mise à jour du timestamp de déconnexion pour cet IMEI (si identifié)
            if imei:
                self.device_repository.update_device_disconnection_time(imei, datetime.now(timezone.utc))

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
