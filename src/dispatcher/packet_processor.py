class PacketProcessor:
    handlers = {
        "AP00": extract_ap00_data,
        "AP01": extract_ap01_data,
        # Ajouter les autres...
    }

    @staticmethod
    def process_packet(packet_type: str, message: str) -> dict:
        handler = PacketProcessor.handlers.get(packet_type)
        if handler:
            return handler(message)
        else:
            print(f"Handler non trouvé pour le type {packet_type}")
            return {}
