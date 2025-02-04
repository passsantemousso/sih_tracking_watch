from typing import Optional, Union, Dict, Any, List
from pydantic import BaseModel, Field
from src.utils.custom_types import PydanticObjectId
from enum import Enum


# Modèle pour le champ `data`
class Data(BaseModel):
    heart_rate: Optional[Union[int, str]] = None
    systolic_pressure: Optional[Union[int, str]] = None
    diastolic_pressure: Optional[Union[int, str]] = None
    spo2: Optional[int] = None
    blood_sugar: Optional[int] = None
    temperature: Optional[Union[float, str]] = None
    gsm_signal: Optional[str] = None
    num_satellites: Optional[str] = None
    battery_level: Optional[str] = None
    remaining_space: Optional[str] = None
    fortification_state: Optional[str] = None
    working_mode: Optional[str] = None
    steps_count: Optional[str] = None
    rolls_frequency: Optional[str] = None
    statistical_period: Optional[str] = None
    total_data_count: Optional[str] = None
    sleep_status: Optional[str] = None
    body_temperature: Optional[Union[float, str]] = None

class DataAPHP(BaseModel):
    heart_rate: Optional[Union[int, str]] = None
    systolic_pressure: Optional[Union[int, str]] = None
    diastolic_pressure: Optional[Union[int, str]] = None
    spo2: Optional[int] = None
    blood_sugar: Optional[int] = None
    temperature: Optional[Union[float, str]] = None

class GPSData(BaseModel):
    latitude: Optional[str] = None
    latitude_direction: Optional[str] = None
    longitude: Optional[str] = None
    longitude_direction: Optional[str] = None
    speed: Optional[str] = None
    gmt_time: Optional[str] = None
    direction_angle: Optional[str] = None

class StatusData(BaseModel):
    gsm_signal: Optional[int] = None
    satellites: Optional[int] = None
    battery_level: Optional[int] = None
    remaining_space: Optional[int] = None
    fortification_state: Optional[int] = None
    working_mode: Optional[int] = None

class BluetoothDevice(BaseModel):
    name: Optional[str] = None
    mac: Optional[str] = None
    signal_strength: Optional[int] = None

class LBSData(BaseModel):
    mcc: Optional[int] = None
    mnc: Optional[int] = None
    lac: Optional[int] = None
    cid: Optional[int] = None

class WiFiData(BaseModel):
    ssid: Optional[str] = None
    mac: Optional[str] = None
    signal_strength: Optional[int] = None

class DataAP01(BaseModel):
    gps: Optional[GPSData] = None
    status: Optional[StatusData] = None
    bluetooth: List[BluetoothDevice] = []
    lbs: List[LBSData] = []
    wifi: List[WiFiData] = []

class DataAP03(BaseModel):
    gsm_signal: Optional[str] = None
    num_satellites: Optional[str] = None
    battery_level: Optional[str] = None
    remaining_space: Optional[str] = None
    fortification_state: Optional[str] = None
    working_mode: Optional[str] = None
    steps_count: Optional[str] = None
    rolls_frequency: Optional[str] = None

class DataAP49(BaseModel):
    heart_rate: Optional[Union[int, str]] = None

class DataAPHT(BaseModel):
    heart_rate: Optional[Union[int, str]] = None
    systolic_pressure: Optional[Union[int, str]] = None
    diastolic_pressure: Optional[Union[int, str]] = None

class DataAP50(BaseModel):
    body_temperature: Optional[Union[float, str]] = None
    battery_level: Optional[str] = None

class DataAP97(BaseModel):
    statistical_period: Optional[str] = None
    total_data_count: Optional[str] = None
    sleep_status: Optional[str] = None


# Modèle principal pour le document
class Device(BaseModel):
    id: PydanticObjectId = Field(alias="_id")
    imei: str
    model: str
    command_type: str
    data: Union[DataAP01 | DataAP03 | DataAP49 | DataAPHT | DataAP50 | DataAP97]
    created_at: str
    updated_at: str

    class Config:
        from_attributes = True
        populate_by_name = True

    def json(self, *args, **kwargs):
        # Serialize the object as a dictionary and then convert to JSON
        return super().model_dump_json(*args, **kwargs).replace('"_id"', '"id"')

    def filter_fields_by_command_type(self) -> Dict[str, Any]:
        """
        Filtre les champs retournés en fonction de la valeur de `command_type`.
        """
        # Champs de base communs à tous les appareils
        base_fields = {
            "id": self.id,
            "imei": self.imei,
            "model": self.model,
            "command_type": self.command_type,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
        }

        # Vérifier si `data` est un sous-modèle Pydantic
        if isinstance(self.data, BaseModel):
            return {**base_fields, "data": self.data.model_dump()}
        else:
            # raise ValueError("Invalid data format. Expected a Pydantic model.")
            return {**base_fields, "data": None}


class CommandType(str, Enum):
    AP01 = "AP01"
    AP02 = "AP02"
    AP03 = "AP03"
    AP04 = "AP04"
    AP05 = "AP05"
    AP16 = "AP16"
    AP49 = "AP49"
    AP50 = "AP50"
    AP97 = "AP97"
    APHT = "APHT"
    APHP = "APHP"