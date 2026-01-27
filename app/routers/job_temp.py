from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.orm import Session
from app.database.db import get_db
from app.models.job import Job
from app.models.crew import Admin, Crew
from app.models.checklist import JobChecklist
from app.schemas.job import JobResponse, ClientJobResponse
from app.schemas.crew import AssignCrewRequest
from app.schemas.checklist import ChecklistUpdate, ChecklistResponse
from app.core.security import get_current_user
from app.core.storage import storage
from typing import List
import random

router = APIRouter()

# ============ ADMIN ENDPOINTS ============

