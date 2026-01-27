from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.models.service import Service
from app.database.db import Base

DATABASE_URL = "postgresql://postgres:root@localhost:5432/packers_db"

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)

# Create tables
Base.metadata.create_all(bind=engine)

# Insert services
db = SessionLocal()

services = [
    {"name": "Emergency Clearance", "description": "Rapid response property clearance for emergency situations"},
    {"name": "Void Property", "description": "Complete clearance and cleaning of vacant properties"},
    {"name": "Hoarder Clean", "description": "Specialized cleaning and clearance for hoarding situations"},
    {"name": "Fire/Flood", "description": "Property clearance and restoration after fire or flood damage"}
]

for service_data in services:
    existing = db.query(Service).filter(Service.name == service_data["name"]).first()
    if not existing:
        service = Service(**service_data)
        db.add(service)

db.commit()
db.close()

print("Services added successfully!")
