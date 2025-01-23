from typing import Any, Dict
from fastapi import APIRouter, HTTPException
from app.db.repositories.device_repo import DeviceRepository
from app.models.device import Device


class DeviceService:

    def __init__(self, device_repo: DeviceRepository):
        self.device_repo = device_repo

    async def create_device(self, device: Device) -> Device:
        return await self.device_repo.create(device)

    async def get_device(self, device_id: str) -> Dict[str, Any]:
        # Récupérer le document brut depuis le référentiel(repo)
        raw_device = await self.device_repo.get_by_id(device_id)

        # Si aucun appareil n'est trouvé, lever une exception
        if not raw_device:
            raise HTTPException(status_code=404, detail="Device not found")

        if isinstance(raw_device, dict):
            try:
                device = Device(**raw_device)

                # Filtrer les champs selon le `command_type` de l'appareil
                filtered_device = device.filter_fields_by_command_type()
            except Exception as e:
                raise HTTPException(status_code=400, detail=f"Invalid device data: {str(e)}")
        else:
            # Si `raw_device` n'est pas un dictionnaire, il est supposé être déjà un objet `Device`
            filtered_device = raw_device.filter_fields_by_command_type()

        # Retourner les données filtrées
        return filtered_device

    async def get_all_devices(self) -> list[dict[str, Any]]:
        raw_devices = await self.device_repo.get_all()

        # Processus de filtrage
        filtered_devices = []
        for raw_device in raw_devices:
            if isinstance(raw_device, dict):
                try:
                    device = Device(**raw_device)
                    filtered_devices.append(device.filter_fields_by_command_type())
                except Exception as e:
                    raise HTTPException(status_code=400, detail=f"Invalid device data: {str(e)}")
            else:
                filtered_devices.append(raw_device.filter_fields_by_command_type())

        return filtered_devices

