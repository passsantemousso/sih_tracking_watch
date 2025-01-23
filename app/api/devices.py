import asyncio
from fastapi import APIRouter, HTTPException
from app.models.device import Device
from app.services.device_service import DeviceService
from app.db.repositories.device_repo import DeviceRepository

router = APIRouter()

device_service = DeviceService(DeviceRepository())

# @router.post("/", response_model=Device)
# async def create_device(device: Device):
#     try:
#         return await device_service.create_device(device)
#     except Exception as e:
#         raise HTTPException(status_code=400, detail=str(e))

@router.get("/all", response_model=list[Device])
async def list_devices():
     return await device_service.get_all_devices()

@router.get("/{device_id}", response_model=Device)
async def get_device(device_id: str):
    return await device_service.get_device(device_id)
