#test
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import auth, job, crew, workflow, admin
from app.database.db import init_db, engine
from app.models.crew import Crew, Admin
from app.models.job import Job
from app.models.photo import JobPhoto
from app.models.invoice import Invoice
from app.models.client import Client
from app.models.checklist import JobChecklist
from sqlalchemy import text
from dotenv import load_dotenv

load_dotenv()

app = FastAPI(
    title="Crew & Admin Management API",
    version="1.0.0",
    description="FastAPI backend for UK-based Crew & Admin Management"
)

app.add_middleware(
    CORSMiddleware,
    allow_origin_regex=r"^http://(localhost|127\.0\.0\.1)(:\d+)?$",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(auth.router, prefix="/api/auth")
app.include_router(job.router, prefix="/api")
app.include_router(crew.router, prefix="/api")
app.include_router(workflow.router, prefix="/api")
app.include_router(admin.router, prefix="/api")

@app.on_event("startup")
def startup():
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        print("✓ Database connected successfully")
        print("✓ table crated (using existing tables)")
    except Exception as e:
        print(f"✗ Database connection failed: {e}")

@app.get("/")
def root():
    return {
        "message": "Crew & Admin Management API",
        "status": "running",
        "version": "1.0.0",
        "port": 8001
    }

@app.get("/health")
def health_check():
    return {
        "backend": "crew_admin_backend",
        "status": "healthy",
        "port": 8001,
        "api_type": "Crew & Admin Management"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
