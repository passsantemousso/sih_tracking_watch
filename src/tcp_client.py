import socket

HOST = '127.0.0.1'  # Adresse IP du serveur
PORT = 5088         # Port du serveur

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client:
    client.connect((HOST, PORT))
    client.sendall(b"IWAP00353456789012345#")
    response = client.recv(1024)
    print(f"Réponse du serveur : {response.decode('utf-8')}")
