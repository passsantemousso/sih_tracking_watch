from typing import Any

from app.db.mongo import database
from app.models.device import Device
from bson import ObjectId
from app.core.config import settings


class DeviceRepository:

    def __init__(self):
        self.collection = database[settings.MONGO_DB_COLLECTION]

    async def create(self, device: Device) -> Device:
        device_dict = device.model_dump()
        result = await self.collection.insert_one(device_dict)
        device.id = result.inserted_id
        return device

    async def get_by_id(self, device_id: str) -> Device | None:
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
