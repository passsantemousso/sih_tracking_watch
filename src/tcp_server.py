import socket
import threading
import datetime
import time

# Configuration du serveur
HOST = '0.0.0.0'  # Écoute sur toutes les interfaces réseau
PORT = 6015  # Port défini pour le protocole
MAX_SIZE = 10 * 1024 * 1024  # 10 Mo

# IMEI
IMEI = "861265062672529"


# Fonction pour traiter chaque connexion client
def handle_client(conn, addr):

    try:
        # Envoyer la commande BP16 dès qu'un appareil se connecte
        send_bp16_command(conn)

        buffer = b""  # Tampon pour stocker les données reçues
        last_activity_time = time.time()  # Pour surveiller les intervalles d'inactivité.

        while True:
            # Recevoir les données de l'appareil
            print("OK - En attente de données...")
            chunk = conn.recv(4096)

            if not chunk:
                print("Aucune donnée reçue, la connexion est peut-être fermée.")

                current_time = time.time()

                if current_time - last_activity_time > 600:  # 10 minutes d'inactivité
                    print(f"Aucune donnée depuis 10 minutes. Déconnexion de {addr}.")
                    break
                else:
                    print(f"En attente de données depuis {addr}...")
                    time.sleep(30)  # Attente continue (ou toute autre action nécessaire)
                    continue

            last_activity_time = time.time()  # Données reçues, réinitialisation de l'inactivité.

            buffer += chunk
            print(f"Reçu {len(chunk)} octets, total : {len(buffer)} octets")

            # Limiter la taille des données pour éviter des dépassements
            if len(buffer) > MAX_SIZE:
                print("Erreur : données reçues dépassent la taille maximale autorisée (10 Mo).")
                break

            # Vérifiez si le message est complet (utilisez "#" comme délimiteur)
            if buffer.endswith(b"#"):
                message = buffer.decode('utf-8')
                print(f"Paquet complet reçu : {message}")

                # Traiter le paquet
                response = process_packet(message)
                if response:
                    conn.sendall(response.encode('utf-8'))
                    print(f"Réponse envoyée à {addr} : {response}")
                else:
                    print(f"Aucune réponse nécessaire pour : {message}")

                buffer = b""  # Réinitialiser le tampon pour le prochain paquet

    except Exception as e:
        print(f"Erreur avec {addr}: {e}")
    finally:
        conn.close()
        print(f"Connexion fermée avec {addr}")

# Fonction pour envoyer une commande BP16
def send_bp16_command(conn):
    # Générer un numéro de journal unique (timestamp en secondes)
    journal_no = datetime.datetime.utcnow().strftime("%H%M%S")
    command = f"IWBP16,{IMEI},{journal_no}#"

    try:
        # Envoyer la commande à la montre connectée
        conn.sendall(command.encode('utf-8'))
        print(f"Commande BP16 envoyée avec succès : {command}")
    except Exception as e:
        print(f"Erreur lors de l'envoi de la commande BP16 : {e}")


# Fonction pour analyser les paquets et générer une réponse
def process_packet(packet):
    if packet.startswith("IWAP00"):
        # Réponse au paquet AP00
        server_time = datetime.datetime.utcnow().strftime("%Y%m%d%H%M%S")
        return f"IWBP00,{server_time},8#"

    elif packet.startswith("IWAP01"):
        # Paquet de localisation (AP01)
        return "IWBP01#"
    elif packet.startswith("IWAP03"):
        # Paquet de maintien de connexion (AP03)
        return "IWBP03#"
        # Vérifiez si c'est une réponse AP16
    elif packet.startswith("IWAP16"):
        journal_no = packet.split(",")[1].strip("#")
        print(f"Réponse reçue pour BP16 avec journal no : {journal_no}")
        # La montre va envoyer des données de localisation après cette réponse

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
        server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1) # Permettre la réutilisation du port
        server.bind((HOST, PORT))
        server.listen()
        print(f"Serveur TCP démarré sur {HOST}:{PORT}...")

        while True:
            # Accepter une nouvelle connexion
            conn, addr = server.accept()
            print(f"Connexion établie avec {addr}")

            # Gérer la connexion dans un thread séparé
            client_thread = threading.Thread(target=handle_client, args=(conn, addr))
            client_thread.start()


# Lancer le serveur
if __name__ == "__main__":
    try:
        start_server()
    except KeyboardInterrupt:
        print("\nServeur arrêté.")
