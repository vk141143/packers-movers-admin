from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class CrewResponse(BaseModel):
    id: str
    email: str
    full_name: str
    phone_number: Optional[str]
    status: str
    is_approved: bool
    created_at: datetime

    class Config:
        from_attributes = True

class AssignCrewRequest(BaseModel):
    crew_id: str
