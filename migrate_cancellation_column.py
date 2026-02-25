 #!/usr/bin/env python3
"""
Add cancellation_reason column to jobs table
"""

from sqlalchemy import create_engine, text
from dotenv import load_dotenv
import os

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    print("ERROR: DATABASE_URL not found in environment variables")
    exit(1)

# Convert asyncpg URL to psycopg2 URL
if DATABASE_URL.startswith("postgresql+asyncpg://"):
    DATABASE_URL = DATABASE_URL.replace("postgresql+asyncpg://", "postgresql://")

print(f"Connecting to database...")

try:
    engine = create_engine(DATABASE_URL)
    
    with engine.connect() as conn:
        print("Adding cancellation_reason column...")
        conn.execute(text("ALTER TABLE jobs ADD COLUMN IF NOT EXISTS cancellation_reason TEXT"))
        
        conn.commit()
        
        print("Migration completed successfully!")
        print("cancellation_reason column added")
        
except Exception as e:
    print(f"Migration failed: {e}")
    exit(1)
