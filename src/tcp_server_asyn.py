import socket
import asyncio
import datetime

class TCPServer:
    def __init__(self, host='0.0.0.0', port=5088):
        self.host = host
        self.port = port

    async def handle_client(self, reader, writer):
        """Gère la communication avec un client de manière asynchrone."""
        addr = writer.get_extra_info('peername')
        print(f"Connexion établie avec {addr}")

        try:
            while True:
                # Recevoir les données du client
                data = await reader.read(1024)
                if not data:
                    print(f"Connexion fermée par le client : {addr}")
                    break

                message = data.decode('utf-8').strip()
                print(f"Données reçues de {addr} : {message}")

                # Traiter le message reçu
                response = self.process_message(message)
                if response:
                    writer.write(response.encode('utf-8'))
                    await writer.drain()
                    print(f"Réponse envoyée à {addr} : {response}")
        except Exception as e:
            print(f"Erreur avec {addr}: {e}")
        finally:
            writer.close()
            await writer.wait_closed()

    @staticmethod
    def process_message(message):
        """Traite les messages reçus et génère une réponse appropriée."""
        if message.startswith("IWAP00"):
            # Exemple de réponse au paquet AP00
            server_time = datetime.datetime.now(datetime.UTC).strftime("%Y%m%d%H%M%S")
            return f"IWBP00,{server_time},8#"
        elif message.startswith("IWAP16"):
            # Exemple de réponse pour un paquet de localisation (AP16)
            return "IWBP16#"
        else:
            print(f"Paquet non reconnu : {message}")
            return None

    async def start(self):
        """Démarre le serveur TCP de manière asynchrone."""
        server = await asyncio.start_server(self.handle_client, self.host, self.port)
        addr = server.sockets[0].getsockname()
        print(f"Serveur TCP démarré sur {addr}...")

        try:
            async with server:
                await server.serve_forever()
        except asyncio.CancelledError:
            print("\nArrêt du serveur...")

if __name__ == "__main__":
    # Créer une instance du serveur et démarrer
    server = TCPServer(host='0.0.0.0', port=6015)
    try:
        asyncio.run(server.start())
    except KeyboardInterrupt:
        print("Serveur arrêté par l'utilisateur.")
