from sqlalchemy import Column, String, Boolean, DateTime
from datetime import datetime
from app.database.db import Base
import uuid

class JobChecklist(Base):
    __tablename__ = "job_checklists"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    job_id = Column(String, nullable=False, unique=True)
    access_gained_successfully = Column(Boolean, default=False)
    waste_verified_with_client = Column(Boolean, default=False)
    no_hazardous_material_found = Column(Boolean, default=False)
    property_protected = Column(Boolean, default=False)
    loading_started_safely = Column(Boolean, default=False)
    completed_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
