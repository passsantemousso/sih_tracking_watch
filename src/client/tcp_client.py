import socket
import time
import os
import logging
import signal
import sys
import json
import threading


# Configurer les logs
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Paramètres du serveur
SERVER_IP = os.getenv("SERVER_IP", "127.0.0.1")
SERVER_PORT = int(os.getenv("SERVER_PORT", 6020))
CONNECTION_TIMEOUT = 10
PING_MESSAGE = "IWKEEPALIVE#"
MAX_RETRIES = 5
RETRY_DELAY = 10  # En secondes
PING_INTERVAL = 60  # Intervalle de ping (en secondes)

def send_keep_alive(client_socket, interval=60):
    while True:
        try:
            client_socket.sendall(PING_MESSAGE.encode())
            logging.info(f"Ping envoyé : {PING_MESSAGE}")
            time.sleep(interval)
        except socket.error as e:
            logging.error(f"Erreur lors de l'envoi du ping : {e}")
            break

def reconnect():
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            client_socket.connect((SERVER_IP, SERVER_PORT))
            logging.info("Connexion rétablie.")
            return client_socket
        except (socket.timeout, ConnectionRefusedError) as e:
            logging.warning(f"Tentative {attempt}/{MAX_RETRIES} échouée : {e}")
            time.sleep(RETRY_DELAY)
    logging.error("Impossible de se reconnecter après plusieurs tentatives.")
    return None

def load_messages(file_path="messages.json"):
    with open(file_path, "r") as f:
        return json.load(f)

# Gestion de l'arrêt du programme (Ctrl+C)
def signal_handler(sig, frame):
    logging.info("Arrêt du programme demandé. Fermeture en cours...")
    sys.exit(0)


signal.signal(signal.SIGINT, signal_handler)


# Fonction pour envoyer un message au serveur
def send_messages_to_server_with_delay(messages: list, delay: int = 5):
    """
    Envoie une liste de messages au serveur via une seule connexion TCP,
    avec un délai spécifié entre chaque message.
    """
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_socket:
            client_socket.settimeout(CONNECTION_TIMEOUT)
            client_socket.connect((SERVER_IP, SERVER_PORT))
            logging.info("Connexion établie avec le serveur.")

            # # Lancer un thread pour le keep-alive
            # ping_thread = threading.Thread(target=send_keep_alive, args=(client_socket, PING_INTERVAL), daemon=True)
            # ping_thread.start()

            for message in messages:
                try:
                    logging.info(f"{message}")
                    client_socket.sendall(message.encode())
                    response = client_socket.recv(1024).decode()
                    if response:
                        logging.info(f"Message envoyé: {message.strip('#')}")
                        logging.info(f"Réponse du serveur: {response}")
                    else:
                        logging.warning("Réponse vide du serveur")
                except socket.error as e:
                    logging.error(f"Erreur lors de l'envoi du message {message}: {e}")
                    break  # Quitter la boucle si une erreur survient

                time.sleep(delay)
    except socket.timeout:
        logging.error("Timeout atteint lors de la tentative de connexion au serveur.")
    except ConnectionRefusedError:
        logging.error("Connexion refusée. Vérifiez que le serveur est actif.")
    except socket.error as e:
        logging.error(f"Erreur réseau : {e}")
    finally:
        logging.info("Connexion avec le serveur fermée.")


def main():
    """Processus principal pour envoyer les messages."""
    MESSAGE_DELAY = 10  # Latence entre chaque message (en secondes)
    CYCLE_DELAY = 120  # Délai entre chaque cycle d'envoi (en secondes)

    logging.info("Démarrage du client TCP...")

    # Charger les messages dynamiquement
    try:
        messages_device = load_messages("messages.json")
        logging.info("Messages chargés depuis le fichier de configuration.")
    except FileNotFoundError:
        logging.error("Le fichier de configuration des messages est introuvable.")
        sys.exit(1)

    while True:
        try:
            logging.info("Début de l'envoi des messages...")
            message_list = list(messages_device.values())

            client_socket = reconnect()
            if client_socket:  # Si la reconnexion réussit
                send_messages_to_server_with_delay(message_list, MESSAGE_DELAY)
                client_socket.close()
            else:
                logging.error("Impossible de se reconnecter au serveur.")
                break

            logging.info(
                f"Tous les messages ont été envoyés. Attente de {CYCLE_DELAY // 60} minutes avant de recommencer...")

            time.sleep(CYCLE_DELAY)  # Attendre avant de recommencer un nouveau cycle
        except KeyboardInterrupt:
            logging.info("Interruption détectée. Fermeture du client TCP...")
            break


if __name__ == "__main__":
    main()
