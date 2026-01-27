from sqlalchemy import Column, Integer, String, DateTime, Boolean
from datetime import datetime
from app.database.db import Base

class Client(Base):
    __tablename__ = "clients"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    password = Column(String, nullable=False)
    full_name = Column(String)
    company_name = Column(String)
    phone_number = Column(String)
    client_type = Column(String)
    address = Column(String)
    is_verified = Column(Boolean, default=False)
    otp = Column(String)
    otp_expiry = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)
