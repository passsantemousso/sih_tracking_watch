import socket
import time

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

# Paramètres du serveur
SERVER_IP = "127.0.0.1"  # Remplacez par l'adresse IP du serveur
SERVER_PORT = 6020      # Remplacez par le port du serveur

def send_message_to_server(message: str):
    """Envoie un message au serveur via une connexion TCP."""
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_socket:
            client_socket.connect((SERVER_IP, SERVER_PORT))
            client_socket.sendall(message.encode())
            response = client_socket.recv(1024).decode()
            print(f"Message envoyé: {message.strip('#')}")
            print(f"Réponse du serveur: {response}")
    except Exception as e:
        print(f"Erreur lors de l'envoi du message: {e}")

def main():
    """Processus principal pour envoyer les messages."""
    while True:
        for command, message in messages.items():
            send_message_to_server(message)
        print("Tous les messages ont été envoyés. Attente de 3 minutes avant de recommencer...")
        time.sleep(180)  # Attendre 3 minutes avant de recommencer le cycle

if __name__ == "__main__":
    main()
