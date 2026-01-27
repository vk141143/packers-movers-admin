from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class JobResponse(BaseModel):
    id: str
    client_id: Optional[str]
    service_type: str
    service_level: str
    vehicle_type: Optional[str]
    property_address: str
    scheduled_date: str
    scheduled_time: str
    property_photos: Optional[str]
    price: float
    additional_notes: Optional[str]
    status: str
    created_at: Optional[datetime]
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True

class ClientJobResponse(BaseModel):
    id: str
    client_id: str
    service_type: str
    service_level: str
    vehicle_type: Optional[str]
    property_address: str
    scheduled_date: str
    scheduled_time: str
    property_photos: Optional[str]
    price: float
    additional_notes: Optional[str]
    status: str
    created_at: Optional[datetime]
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True
