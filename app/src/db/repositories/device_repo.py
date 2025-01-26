from src.db.mongo import database
from src.models.device import Device
from bson import ObjectId
from src.core.config import settings
from datetime import datetime
import logging

class DeviceRepository:

    def __init__(self):
        self.collection = database[settings.MONGO_DB_COLLECTION]

    async def create(self, device: Device) -> Device:
        device_dict = device.model_dump()
        result = await self.collection.insert_one(device_dict)
        device.id = result.inserted_id
        return device

    async def get_by_id(self, device_id: str) -> Device | None:
        if not ObjectId.is_valid(device_id):
            raise ValueError(f"Invalid ObjectId: {device_id}")

        device = await self.collection.find_one({"_id": ObjectId(device_id)})
        if device:
            device["id"] = str(device["_id"])
            return Device(**device)

        return None

    async def get_all(self, limit: int = 100) -> list[Device]:
        devices = []
        async for device in self.collection.find().limit(limit):
            device["id"] = str(device["_id"])
            devices.append(Device(**device))
        return devices

    async def search(
            self, imei: str = None,
            model: str = None,
            command_type: str = None,
            created_at_start: str = None,
            created_at_end: str = None,
            limit: int = 100) -> list[Device]:

        query = {}

        # Ajout des filtres dynamiques
        if imei:
            query["imei"] = imei
        if model:
            query["model"] = model
        if command_type:
            query["command_type"] = command_type
        if created_at_start or created_at_end:
            query["created_at"] = {}
            if created_at_start:
                query["created_at"]["$gte"] = created_at_start.isoformat()
            if created_at_end:
                query["created_at"]["$lte"] = created_at_end.isoformat()

        devices = []
        async for device in self.collection.find(query).limit(limit):
            device["id"] = str(device["_id"])
            devices.append(Device(**device))

        return devices

    async def get_latest_by_imei_and_command_type(self, imei: str, command_type: str) -> Device | None:
        """
        Récupère le dernier enregistrement correspondant à un IMEI et un type de commande.
        """
        query = {"imei": imei, "command_type": command_type}
        # Tri par date de création, décroissant
        device = await self.collection.find_one(query, sort=[("created_at", -1)])

        if device:
            # Convertir l'_id en str pour correspondre au modèle
            device["id"] = str(device["_id"])
            return Device(**device)

        return None
