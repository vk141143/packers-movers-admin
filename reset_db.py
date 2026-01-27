from app.database.db import engine, Base
from app.models.crew import Crew, Admin
from app.models.job import Job
from app.models.invoice import Invoice

# Drop all tables
Base.metadata.drop_all(bind=engine)
print("All tables dropped")

# Create all tables with new schema
Base.metadata.create_all(bind=engine)
print("All tables created with new schema")