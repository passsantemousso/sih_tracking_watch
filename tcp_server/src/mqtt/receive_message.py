import paho.mqtt.client as mqtt

from src.core.config import settings


# Callback lorsque la connexion au broker est réussie
def on_connect(client_id, userdata, flags, rc):
    print(f"Connecté au broker avec le code de retour {rc}")
    client.subscribe("health_data_topic")  # S'abonner au topic

# Callback lorsque le client reçoit un message
def on_message(client_id, userdata, msg):
    print(f"Message reçu sur le topic {msg.topic}: {msg.payload.decode()}")

# Configuration du client MQTT
client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2, protocol=mqtt.MQTTv5)
client.on_connect = on_connect
client.on_message = on_message

# Connexion au broker MQTT (adresse du broker à adapter)
client.connect(settings.MQTT_BROKER, 1883, 60)

# Lancer la boucle pour recevoir les messages
client.loop_forever()
