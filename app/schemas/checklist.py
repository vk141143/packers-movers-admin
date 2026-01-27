from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class ChecklistUpdate(BaseModel):
    verify_property_access: Optional[bool] = None
    pack_and_remove_items: Optional[bool] = None
    clean_property: Optional[bool] = None
    get_council_signoff: Optional[bool] = None

class ChecklistResponse(BaseModel):
    id: str
    job_id: str
    verify_property_access: bool
    pack_and_remove_items: bool
    clean_property: bool
    get_council_signoff: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
