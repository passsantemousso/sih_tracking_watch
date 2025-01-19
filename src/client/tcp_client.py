import socket
import time
import os
import logging

# Configurer les logs
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Définir les messages à envoyer
messages = {
    "AP00": "IWAP00861265062672529#",
    "AP01": "",
    "AP16": "",
    "AP02": "",
    "AP03": "IWAP03,08000007000001,00022,00#",
    "AP49": "IWAP49,68#",
    "APHT": "IWAPHT,60,130,85#",
    "APHP": "IWAPHP,83,117,79,98,0.0,36.7#",
    "AP50": "IWAP50,36.7,90#",
    "AP97": "IWAP97,2300@0800,109,001222222113...#"
}

# Paramètres du serveur (utilisation des variables d'environnement pour Docker)
SERVER_IP = os.getenv("SERVER_IP", "127.0.0.1")  # Utilise 127.0.0.1 par défaut si non défini
SERVER_PORT = int(os.getenv("SERVER_PORT", 6020))  # Utilise le port 6020 par défaut si non défini

# Fonction pour envoyer un message au serveur
def send_message_to_server(message: str):
    """Envoie un message au serveur via une connexion TCP."""
    attempt = 0
    while attempt < 5:  # Essayer 5 fois en cas d'échec
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_socket:
                client_socket.connect((SERVER_IP, SERVER_PORT))
                client_socket.sendall(message.encode())
                response = client_socket.recv(1024).decode()
                if response:
                    logging.info(f"Message envoyé: {message.strip('#')}")
                    logging.info(f"Réponse du serveur: {response}")
                    return
                else:
                    logging.warning("Réponse vide du serveur")
        except (socket.timeout, socket.error) as e:
            logging.error(f"Erreur lors de l'envoi du message (tentative {attempt+1}/5): {e}")
            attempt += 1
            time.sleep(5)  # Attendre avant de réessayer
    logging.error("Échec de la connexion après 5 tentatives.")

def main():
    """Processus principal pour envoyer les messages."""
    while True:
        logging.info("Début de l'envoi des messages...")
        for command, message in messages.items():
            send_message_to_server(message)
        logging.info("Tous les messages ont été envoyés. Attente de 3 minutes avant de recommencer...")
        time.sleep(180)  # Attendre 3 minutes avant de recommencer le cycle

if __name__ == "__main__":
    main()
