from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os
from pathlib import Path
from dotenv import load_dotenv

# Get the directory where this file is located
BASE_DIR = Path(__file__).resolve().parent.parent.parent
ENV_FILE = BASE_DIR / ".env"

# Load .env file from the project root
if ENV_FILE.exists():
    load_dotenv(ENV_FILE, override=True)
    print(f"Loaded .env from: {ENV_FILE}")
else:
    print(f"Warning: .env file not found at {ENV_FILE}")
    load_dotenv(override=True)  # Try to load from current directory as fallback

DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    raise ValueError("DATABASE_URL environment variable is not set. Please check your .env file or environment variables.")

print(f"Using DATABASE_URL: {DATABASE_URL[:50]}...")

engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,
    pool_recycle=3600,
    pool_size=5,
    max_overflow=10,
    connect_args={"connect_timeout": 10} if "postgresql" in DATABASE_URL else {}
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def init_db():
    Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
