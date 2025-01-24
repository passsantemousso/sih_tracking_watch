from dataclasses import dataclass

@dataclass
class AP01Packet:
    latitude: str
    longitude: str
    speed: float
    gmt_time: str
    direction_angle: float
    # Ajouter d'autres attributs...
