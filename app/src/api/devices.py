import logging
from typing import List, Dict, Any, Optional
from fastapi import APIRouter, Query, Depends
from src.models.device import Device
from src.services.device_service import DeviceService
from src.db.repositories.device_repo import DeviceRepository

router = APIRouter()

device_service = DeviceService(DeviceRepository())

# @router.post("/", response_model=Device)
# async def create_device(device: Device):
#     try:
#         return await device_service.create_device(device)
#     except Exception as e:
#         raise HTTPException(status_code=400, detail=str(e))

@router.get("/search", response_model=List[Dict[str, Any]])
async def search_devices(
    imei: Optional[str] = Query(None),
    model: Optional[str] = Query(None),
    command_type: Optional[str] = Query(None),
    created_at_start: Optional[str] = Query(None, description="Format: DD-MM-YYYY"),
    created_at_end: Optional[str] = Query(None, description="Format: DD-MM-YYYY"),
    limit: int = Query(100, ge=1),
):
    return await device_service.search_devices(
        imei=imei,
        model=model,
        command_type=command_type,
        created_at_start=created_at_start,
        created_at_end=created_at_end,
        limit=limit,
    )

@router.get("/latest", response_model=Device)
async def get_latest_device(
    imei: str = Query(..., description="IMEI number of the device"),
    command_type: str = Query(..., description="Command type of the device")
):
    """
    Récupère le dernier enregistrement pour un IMEI et un type de commande.
    """
    return await device_service.get_latest_device(imei, command_type)

@router.get("/all", response_model=list[Device])
async def list_devices():
     return await device_service.get_all_devices()

@router.get("/{device_id}", response_model=Device)
async def get_device(device_id: str):
    return await device_service.get_device(device_id)






