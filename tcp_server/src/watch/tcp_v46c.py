import socket


def send_command_to_watch(device_id, server_ip, server_port, watch_ip, watch_port):
    """
    Envoie une commande à la montre pour configurer son IP et son port de serveur.
    :param device_id: ID de l'appareil (ex: '8800000015')
    :param server_ip: IP du serveur où la montre doit envoyer ses données
    :param server_port: Port du serveur
    :param watch_ip: Adresse IP actuelle de la montre
    :param watch_port: Port d'écoute actuel de la montre
    """

    command = f"[SG*{device_id}*{len(f'IP,{server_ip},{server_port}'):04X}*IP,{server_ip},{server_port}]"
    print(command)

    try:
        # Création de la connexion socket avec la montre
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.connect((watch_ip, watch_port))
            sock.sendall(command.encode('utf-8'))
            print(f"Commande envoyée : {command}")

            # Attendre la réponse de la montre (si applicable)
            response = sock.recv(1024)
            print(f"Réponse de la montre : {response.decode('utf-8')}")

    except Exception as e:
        print(f"Erreur lors de l'envoi de la commande : {e}")


# Exemple d'utilisation
if __name__ == "__main__":
    DEVICE_ID = "9705267607"  # Remplacez par l'ID de votre montre
    SERVER_IP = "84.247.167.15"  # IP du serveur à configurer
    SERVER_PORT = 6020  # Port du serveur
    WATCH_IP = "192.168.1.50"  # Adresse IP actuelle de la montre
    WATCH_PORT = 5900  # Port actuel d'écoute de la montre

    send_command_to_watch(DEVICE_ID, SERVER_IP, SERVER_PORT, WATCH_IP, WATCH_PORT)
