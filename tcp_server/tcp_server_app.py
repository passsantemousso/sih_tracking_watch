import asyncio
import signal
import logging
from src.logg.logging_config import configure_logging
from src.gateway.tcp_server_asyn import TCPServerAsync
from src.mqtt.mqtt_consumer import MqttConsumer
from src.mongodb.mongodb_helper import MongoDBHelper
from src.paquets.packet_processor import PacketProcessor
from src.mqtt.mqtt_handler import MQTTHandler


# Configure le logging
configure_logging()

# Création d'un logger pour ce module
logger = logging.getLogger(__name__)

async def main():
    try:
        logger.info("Démarrage du programme")

        # Initialisation des composants
        packet_processor = PacketProcessor()
        mqtt_handler = MQTTHandler()
        mongo_helper = MongoDBHelper(is_debug=True)

        mongo_helper.test_connection()
        mongo_helper.ensure_collection_exists()
        logger.info("Connexion à MongoDB réussie et collection vérifiée")

        # Instanciation du repository pour gérer les devices
        from src.mongodb.repository.device_repository import DeviceRepository
        device_repository = DeviceRepository(mongo_helper, is_debug=True)

        # Instanciation du service pour envoyer les commandes vers la montre
        from src.commands.watch_command import WatchCommandService
        watch_command_service = WatchCommandService()

        consumer = MqttConsumer(mongodb_helper=mongo_helper, packet_processor=packet_processor, is_debug=True)
        mqtt_handler.connect()

        # Tâches pour les serveurs
        mqtt_handler_task = asyncio.create_task(mqtt_handler.mqtt_loop(), name="MQTT Loop Task")
        consumer.start()
        tcp_server = TCPServerAsync(
            mqtt_handler,
            packet_processor,
            device_repository,
            watch_command_service,
            is_debug=True
        )
        tcp_task = asyncio.create_task(tcp_server.start(), name="TCP Task")

        logger.info(f"Tâches principales créées : "
                    f"MQTT Handler Task ID: {id(mqtt_handler_task)},"
                    f"TCP Task ID: {id(tcp_task)}"
        )

        try:
            await asyncio.gather(mqtt_handler_task, tcp_task)
        except Exception as e:
            logger.error(f"Erreur dans les tâches : {e}", exc_info=True)

        # Gestion des signaux pour un arrêt propre
        # stop_event = asyncio.Event()
        # signal_handled = False
        #
        # def handle_stop_signal():
        #     nonlocal signal_handled
        #     if not signal_handled:
        #         logger.warning(f"Signal d'arrêt reçu (probablement {signal.SIGTERM})")
        #         signal_handled = True
        #         stop_event.set()
        #
        # for sig in (signal.SIGINT, signal.SIGTERM):
        #     asyncio.get_running_loop().add_signal_handler(sig, lambda: handle_stop_signal())
        #
        # await stop_event.wait()
        # logger.info("Arrêt demandé, nettoyage en cours...")

        # Arrêt propre des serveurs
        # mqtt_task.cancel()
        # tcp_task.cancel()
        # await asyncio.gather(mqtt_task, tcp_task, return_exceptions=True)
        # logger.info("Tâches terminées proprement.")

    except Exception as e:
        logger.error(f"Erreur dans le programme principal : {e}", exc_info=True)
    finally:
        logger.info("Programme terminé.")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Interruption clavier détectée.")
    finally:
        print("Programme terminé, retour au terminal.")
