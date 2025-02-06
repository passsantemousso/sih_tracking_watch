from typing import Any, Dict, Optional, List
from fastapi import HTTPException
from src.db.repositories.device_repo import DeviceRepository
from src.models.device import Device
from bson import ObjectId
from datetime import datetime, timedelta


class DeviceService:

    def __init__(self, device_repo: DeviceRepository):
        self.device_repo = device_repo

    @staticmethod
    def parse_date(date_str: Optional[str], end_of_day: bool = False) -> Optional[datetime]:
        """
        Convertit une date au format DD-MM-YYYY en datetime.
        Si `end_of_day` est True, ajuste l'heure à 23:59:59.
        """
        if date_str:
            try:
                date = datetime.strptime(date_str, "%d-%m-%Y")
                if end_of_day:
                    date += timedelta(hours=23, minutes=59, seconds=59)
                return date
            except ValueError:
                raise HTTPException(
                    status_code=400,
                    detail=f"Invalid date format for '{date_str}'. Expected format: DD-MM-YYYY."
                )
        return None

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

    async def create_device(self, device: Device) -> Device:
        return await self.device_repo.create(device)

    async def get_device(self, device_id: str) -> Dict[str, Any]:
        try:
            # Vérifier si l'identifiant est valide
            if not ObjectId.is_valid(device_id):
                raise HTTPException(status_code=400, detail=f"Invalid device ID: {device_id}")
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
            sort_field: str = "created_at",
            sort_order: int = -1
    ) -> List[Dict[str, Any]]:

        start_date = self.parse_date(created_at_start)
        end_date = self.parse_date(created_at_end, end_of_day=True)

        try:
            # Appel de la méthode de recherche dans le référentiel
            raw_devices = await self.device_repo.search(
                imei=imei,
                model=model,
                command_type=command_type,
                created_at_start=start_date,
                created_at_end=end_date,
                limit=limit,
                sort_field=sort_field,
                sort_order=sort_order
            )

            # Processus de filtrage
            return self._filter_devices(raw_devices)

        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error during device search: {str(e)}")


    async def get_latest_device(self, imei: str, command_type: str) -> Device:
        """
        Appelle le repository pour récupérer le dernier enregistrement.
        """
        device = await self.device_repo.get_latest_by_imei_and_command_type(imei, command_type)

        if not device:
            raise HTTPException(
                status_code=404,
                detail=f"No device found for IMEI {imei} and command type {command_type}."
            )

        return device