from sqlalchemy import Column, Integer, String, DateTime, Boolean
from datetime import datetime
from app.database.db import Base
import uuid

class Crew(Base):
    __tablename__ = "crew"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    email = Column(String, unique=True, index=True, nullable=False)
    full_name = Column(String, nullable=False)
    password_hash = Column(String, nullable=False)
    phone_number = Column(String)
    drivers_license = Column(String)
    dbs_certificate = Column(String)
    proof_of_address = Column(String)
    insurance_certificate = Column(String)
    right_to_work = Column(String)
    is_approved = Column(Boolean, default=False)
    status = Column(String, default="available")  # available, assigned, unavailable
    reset_otp = Column(String, nullable=True)
    reset_otp_expiry = Column(DateTime, nullable=True)
    reset_token = Column(String, nullable=True)
    reset_token_expiry = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class Admin(Base):
    __tablename__ = "admins"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    email = Column(String, unique=True, index=True, nullable=False)
    full_name = Column(String, nullable=False)
    password_hash = Column(String, nullable=False)
    organization_name = Column(String, nullable=True)
    phone_number = Column(String, nullable=True)
    contact_person = Column(String, nullable=True)
    department = Column(String, nullable=True)
    business_address = Column(String, nullable=True)
    reset_otp = Column(String, nullable=True)
    reset_otp_expiry = Column(DateTime, nullable=True)
    reset_token = Column(String, nullable=True)
    reset_token_expiry = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
