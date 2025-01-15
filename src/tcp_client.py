import socket
import time

# Définir les messages à envoyer
messages = {
    "AP00": "IWAP00,latitude=40.7128,longitude=-74.0060#",
    "AP01": "IWAP01,latitude=40.7128,longitude=-74.0060,accuracy=15#",
    "AP16": "IWAP16,latitude=40.7128,longitude=-74.0060,altitude=10#",
    "AP02": "IWAP02,zh_cn|2@bt1|bc-57-29-00-25-d7|52&bt2|bc-57-29-00-25-e5|55,0,7,460,0,9520|3671|13,9520|3672|12,9520|3673|11,9520|3674|10,9520|3675|9,9520|3676|8,9520|3677|7,4,1|D8-24-BD-79-FA-1F|59&2|3C-46-D8-6D-CE-01|81&3|0C-4C-39-1A-7C-65|69&4|70-A8-E3-5D-D7-C0|65#",
    "AP03": "IWAP03,06000908000102,5555,30#",
    "AP49": "IWAP49,68#",
    "APHT": "IWAPHT,60,130,85#",
    "APHP": "IWAPHP,60,130,85,95,90,36.5,,,,,,,#",
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
            time.sleep(10)  # Attendre 10 secondes entre chaque envoi
        print("Tous les messages ont été envoyés. Attente de 3 minutes avant de recommencer...")
        time.sleep(180)  # Attendre 3 minutes avant de recommencer le cycle

if __name__ == "__main__":
    main()
