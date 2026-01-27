from sqlalchemy import Column, String, DateTime
from datetime import datetime
from app.database.db import Base
import uuid

class JobPhoto(Base):
    __tablename__ = "job_photos"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    job_id = Column(String, nullable=False)
    photo_url = Column(String, nullable=False)
    type = Column(String, nullable=False)  # "before" or "after"
    timestamp = Column(DateTime, default=datetime.utcnow)
