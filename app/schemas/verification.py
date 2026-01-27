from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

class PhotoResponse(BaseModel):
    id: str
    photo_url: str
    type: str
    timestamp: datetime

    class Config:
        from_attributes = True

class JobVerificationResponse(BaseModel):
    job_id: str
    service_type: str
    sla_level: str
    scheduled_date: str
    completed_at: Optional[datetime]
    pickup_address: str
    delivery_address: Optional[str]
    assigned_crew_id: Optional[str]
    photos: List[PhotoResponse]
