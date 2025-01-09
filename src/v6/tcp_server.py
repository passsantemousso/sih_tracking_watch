import socket


def start_tcp_server(host='0.0.0.0', port=6020):
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((host, port))
    server_socket.listen(5)
    print(f"Server is listening on {host}:{port}")

    while True:
        client_socket, client_address = server_socket.accept()
        print(f"Connection established with {client_address}")
        data = client_socket.recv(1024).decode('utf-8')
        print(f"Data received: {data}")

        # Analyse des données reçues
        if data.startswith('[CS') and 'UD' in data:
            process_data(data)

        # Répondre à la montre si nécessaire (par ex. pour maintenir la connexion)
        if 'LK' in data:
            client_socket.send(data.encode('utf-8'))  # Réponse selon le protocole

        client_socket.close()


def process_data(data):
    # Parse les données selon le format décrit
    parts = data.strip('[]').split('*')
    if len(parts) >= 4:
        device_id = parts[1]
        command = parts[3]
        if command.startswith('UD'):
            positioning_data = command.split(',')[1:]
            save_to_database(device_id, positioning_data)


def save_to_database(device_id, positioning_data):
    # Implémentez l'enregistrement en base de données ici
    print(f"Saving data for device {device_id}: {positioning_data}")
    # Exemple : Insérez les données dans une table SQL


if __name__ == '__main__':
    start_tcp_server(port=6020)
