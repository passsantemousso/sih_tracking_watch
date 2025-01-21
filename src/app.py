import asyncio
import signal
from gateway.tcp_server_asyn import TCPServer
from mqtt.mqtt_consumer import MqttConsumer
from mongodb.mongodb_helper import MongoDBHelper
from paquets.packet_processor import PacketProcessor
from mqtt.mqtt_handler import MQTTHandler


async def main():
    # Initialisation des composants
    packet_processor = PacketProcessor()
    mqtt_handler = MQTTHandler()
    # Connexion au broker MQTT
    mqtt_handler.connect()

    mongo_helper = MongoDBHelper()

    mongo_helper.test_connection()

    # Vérifier ou créer la collection
    mongo_helper.ensure_collection_exists()

    consumer = MqttConsumer(mongo_helper, packet_processor)

    # Tâches pour les serveurs
    mqtt_task = asyncio.create_task(asyncio.to_thread(consumer.start))
    tcp_server = TCPServer(mqtt_handler, packet_processor)
    tcp_task = asyncio.create_task(tcp_server.start())

    # Gestion des signaux pour un arrêt propre
    stop_event = asyncio.Event()
    signal_handled = False  # Pour éviter plusieurs appels du gestionnaire

    def handle_stop_signal():
        nonlocal signal_handled
        if not signal_handled:
            print("Arrêt signalé, fermeture des serveurs...")
            signal_handled = True
            stop_event.set()

    # Capturer SIGINT et SIGTERM
    for sig in (signal.SIGINT, signal.SIGTERM):
        asyncio.get_running_loop().add_signal_handler(sig, lambda: handle_stop_signal())

    # Attendre le signal d'arrêt
    await stop_event.wait()

    # Arrêt propre des serveurs
    print("Arrêt des tâches en cours...")
    # mqtt_task.cancel()
    tcp_task.cancel()

    # Terminer proprement les tâches
    await asyncio.gather(mqtt_task, tcp_task, return_exceptions=True)
    print("Serveurs arrêtés proprement.")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Interruption clavier détectée.")
    finally:
        print("Programme terminé, retour au terminal.")
