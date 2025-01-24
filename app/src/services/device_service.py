from typing import Any, Dict, Optional, List
from fastapi import HTTPException
from src.db.repositories.device_repo import DeviceRepository
from src.models.device import Device


class DeviceService:

    def __init__(self, device_repo: DeviceRepository):
        self.device_repo = device_repo

    async def create_device(self, device: Device) -> Device:
        return await self.device_repo.create(device)

    async def get_device(self, device_id: str) -> Dict[str, Any]:
        try:
            raw_device = await self.device_repo.get_by_id(device_id)
        except ValueError as e:
            raise HTTPException(status_code=400, detail=str(e))

        if not raw_device:
            raise HTTPException(status_code=404, detail="Device not found")

        return self._filter_device(raw_device)

    async def get_all_devices(self) -> list[dict[str, Any]]:
        raw_devices = await self.device_repo.get_all()
        return self._filter_devices(raw_devices)

    async def search_devices(
            self,
            imei: Optional[str] = None,
            model: Optional[str] = None,
            command_type: Optional[str] = None,
            created_at_start: Optional[str] = None,
            created_at_end: Optional[str] = None,
            limit: int = 100,
    ) -> List[Dict[str, Any]]:
        try:
            # Appel de la méthode de recherche dans le référentiel
            raw_devices = await self.device_repo.search(
                imei=imei,
                model=model,
                command_type=command_type,
                created_at_start=created_at_start,
                created_at_end=created_at_end,
                limit=limit,
            )

            # Processus de filtrage
            return self._filter_devices(raw_devices)

        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error during device search: {str(e)}")

    @staticmethod
    def _filter_device(raw_device: Dict[str, Any]) -> Dict[str, Any]:
        """
        Filtre un seul appareil selon le `command_type`.
        """
        if isinstance(raw_device, dict):
            try:
                device = Device(**raw_device)
                return device.filter_fields_by_command_type()
            except Exception as e:
                raise HTTPException(status_code=400, detail=f"Invalid device data: {str(e)}")
        else:
            return raw_device.filter_fields_by_command_type()


    def _filter_devices(self, raw_devices: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Filtre une liste d'appareils selon leur `command_type`.
        """
        return [self._filter_device(raw_device) for raw_device in raw_devices]