from sqlalchemy import Column, Integer, String, DateTime, Boolean
from datetime import datetime
from app.database.db import Base
import uuid
from sqlalchemy.dialects.postgresql import UUID

class Client(Base):
    __tablename__ = "clients"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    password = Column(String, nullable=False)
    full_name = Column(String)
    company_name = Column(String)
    contact_person_name = Column(String)
    department = Column(String)
    phone_number = Column(String)
    client_type = Column(String)
    business_address = Column(String)
    is_verified = Column(Boolean, default=False)
    otp = Column(String)
    otp_expiry = Column(DateTime)
    otp_method = Column(String)
    reset_otp = Column(String)
    reset_otp_expiry = Column(DateTime)
    reset_token = Column(String)
    reset_token_expiry = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)
