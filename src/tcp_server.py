import socket
import threading

# Configuration du serveur
HOST = '0.0.0.0'  # Écoute sur toutes les interfaces réseau
PORT = 6015  # Port défini pour le protocole


# Fonction pour traiter chaque connexion client
def handle_client(conn, addr):
    print(f"Nouvelle connexion depuis {addr}")
    try:
        while True:
            # Recevoir les données de l'appareil
            data = conn.recv(1024)
            if not data:
                break  # Connexion fermée par le client

            message = data.decode('utf-8').strip()
            print(f"Données reçues de {addr} : {message}")

            # Analyse du paquet et préparation de la réponse
            response = process_packet(message)

            if response:
                conn.sendall(response.encode('utf-8'))
                print(f"Réponse envoyée à {addr} : {response}")
            else:
                print(f"Aucune réponse nécessaire pour : {message}")

    except Exception as e:
        print(f"Erreur avec {addr}: {e}")
    finally:
        conn.close()
        print(f"Connexion fermée avec {addr}")


# Fonction pour analyser les paquets et générer une réponse
def process_packet(packet):
    if packet.startswith("IWAP00"):
        # Paquet de connexion (AP00)
        return "IWBP00,20250108120000,8#"
    elif packet.startswith("IWAP01"):
        # Paquet de localisation (AP01)
        return "IWBP01#"
    elif packet.startswith("IWAP03"):
        # Paquet de maintien de connexion (AP03)
        return "IWBP03#"
    elif packet.startswith("IWAP49"):
        # Paquet de rythme cardiaque (AP49)
        heart_rate = packet.split(",")[1].strip("#")
        print(f"Rythme cardiaque reçu : {heart_rate} bpm")
        return "IWBP49#"
    else:
        print(f"Paquet non reconnu : {packet}")
        return None  # Pas de réponse pour les paquets inconnus


# Fonction principale pour démarrer le serveur
def start_server():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server:
        server.bind((HOST, PORT))
        server.listen()
        print(f"Serveur TCP démarré sur {HOST}:{PORT}...")

        while True:
            # Accepter une nouvelle connexion
            conn, addr = server.accept()
            # Gérer la connexion dans un thread séparé
            client_thread = threading.Thread(target=handle_client, args=(conn, addr))
            client_thread.start()


# Lancer le serveur
if __name__ == "__main__":
    try:
        start_server()
    except KeyboardInterrupt:
        print("\nServeur arrêté.")
