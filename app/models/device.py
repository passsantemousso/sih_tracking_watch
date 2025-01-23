from typing import Optional, Union, Dict, Any
from pydantic import BaseModel, Field
from app.utils.custom_types import PydanticObjectId


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
    data: Union[DataAPHP | DataAP03 | DataAP49 | DataAPHT | DataAP50 | DataAP97]
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

        # Retourner les champs de base avec les données directement
        return {**base_fields, "data": self.data.model_dump()}

