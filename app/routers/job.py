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

# ============ CREW ENDPOINTS ============

@router.get("/crew/jobs", tags=["Crew"], summary="My Jobs")
async def get_crew_jobs(
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    from sqlalchemy import text
    from datetime import datetime, timedelta
    
    crew = db.query(Crew).filter(Crew.email == current_user.get("sub")).first()
    if not crew:
        raise HTTPException(status_code=403, detail="Crew access required")
    
    jobs = db.query(Job).filter(Job.assigned_crew_id == crew.id).order_by(Job.created_at.desc()).all()
    
    result = []
    for job in jobs:
        # Get SLA hours from service level
        sla_hours = 24  # default
        try:
            sla_result = db.execute(
                text("SELECT sla_hours FROM service_levels WHERE id = :id"),
                {"id": job.service_level}
            ).fetchone()
            if sla_result:
                sla_hours = sla_result[0]
        except:
            pass
        
        # Calculate SLA deadline
        sla_deadline = job.created_at + timedelta(hours=sla_hours)
        now = datetime.utcnow()
        
        if job.status == "job_completed":
            # Job completed - check if completed within SLA time
            completion_time = job.updated_at
            if completion_time <= sla_deadline:
                time_remaining = "SLA Met"
                countdown_timer = "On Time"
            else:
                time_remaining = "SLA Breached"
                countdown_timer = "Overdue"
        else:
            # Job in progress - calculate remaining time
            time_diff = sla_deadline - now
            if time_diff.total_seconds() > 0:
                hours_left = int(time_diff.total_seconds() // 3600)
                minutes_left = int((time_diff.total_seconds() % 3600) // 60)
                time_remaining = f"{hours_left}h {minutes_left}m"
                countdown_timer = "On Time"
            else:
                # Overdue
                time_diff = now - sla_deadline
                hours_over = int(time_diff.total_seconds() // 3600)
                minutes_over = int((time_diff.total_seconds() % 3600) // 60)
                time_remaining = f"-{hours_over}h {minutes_over}m"
                countdown_timer = "Overdue"
        
        result.append({
            "job_id": job.id,
            "property_address": job.property_address,
            "scheduled_date": job.preferred_date if job.preferred_date else "",
            "scheduled_time": job.preferred_time if job.preferred_time else "",
            "status": job.status,
            "time_remaining": time_remaining,
            "countdown_timer": countdown_timer
        })
    
    return result

@router.get("/crew/jobs/{job_id}", tags=["Crew"], summary="Get Job Details by ID")
async def get_crew_job_by_id(
    job_id: str,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    from app.models.client import Client
    
    crew = db.query(Crew).filter(Crew.email == current_user.get("sub")).first()
    if not crew:
        raise HTTPException(status_code=403, detail="Crew access required")
    
    job = db.query(Job).filter(Job.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    
    if job.assigned_crew_id != crew.id:
        raise HTTPException(status_code=403, detail="This job is not assigned to you")
    
    # Get client details
    client = db.query(Client).filter(Client.id == job.client_id).first()
    
    return {
        "job_id": job.id,
        "job_reference": f"PROP-{job.created_at.year}-{str(job.id)[:8].upper()}-EMERG" if job.created_at else f"PROP-{str(job.id)[:8].upper()}",
        "client_name": client.company_name if client else "Unknown",
        "service_type": getattr(job, 'service_type', 'emergency clearance'),
        "scheduled_date": job.preferred_date if job.preferred_date else "",
        "scheduled_time": job.preferred_time if job.preferred_time else "",
        "property_address": job.property_address,
        "property_type": getattr(job, 'property_type', 'flat'),
        "property_size": getattr(job, 'property_size', 'M'),
        "priority": getattr(job, 'urgency_level', 'standard'),
        "status": job.status,
        "latitude": job.latitude,
        "longitude": job.longitude
    }

@router.patch("/crew/jobs/{job_id}/arrive", tags=["Crew"])
async def crew_arrive(
    job_id: str,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    crew = db.query(Crew).filter(Crew.email == current_user.get("sub")).first()
    if not crew:
        raise HTTPException(status_code=403, detail="Crew access required")
    
    job = db.query(Job).filter(Job.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    
    if job.assigned_crew_id != crew.id:
        raise HTTPException(status_code=403, detail="This job is not assigned to you")
    
    if job.status != "crew_assigned":
        raise HTTPException(status_code=400, detail=f"Job must be in crew_assigned status. Current status: {job.status}")
    
    job.status = "crew_arrived"
    db.commit()
    return {"message": "Crew arrived", "status": job.status}

@router.post("/crew/jobs/{job_id}/upload-before-photo", tags=["Crew"])
async def upload_before_photo(
    job_id: str,
    photos: List[UploadFile] = File(default=[]),
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    crew = db.query(Crew).filter(Crew.email == current_user.get("sub")).first()
    if not crew:
        raise HTTPException(status_code=403, detail="Crew access required")
    
    job = db.query(Job).filter(Job.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    
    if job.assigned_crew_id != crew.id:
        raise HTTPException(status_code=403, detail="This job is not assigned to you")
    
    if job.status != "crew_arrived":
        raise HTTPException(status_code=400, detail=f"Job must be in crew_arrived status. Current status: {job.status}")
    
    from app.models.photo import JobPhoto
    uploaded_files = []
    for photo in photos:
        if photo.filename:
            photo_url = storage.upload_job_photo(photo.file, job_id, "before", photo.filename)
            if photo_url:
                uploaded_files.append(photo_url)
                job_photo = JobPhoto(
                    job_id=job_id,
                    photo_url=photo_url,
                    type="before"
                )
                db.add(job_photo)
    
    job.status = "before_photo"
    db.commit()
    
    # Auto-create checklist for this job
    from app.models.checklist import JobChecklist
    existing_checklist = db.query(JobChecklist).filter(JobChecklist.job_id == job_id).first()
    if not existing_checklist:
        checklist = JobChecklist(job_id=job_id)
        db.add(checklist)
        db.commit()
    
    return {"message": "Before photos uploaded", "status": job.status, "uploaded_count": len(uploaded_files)}

@router.get("/crew/jobs/{job_id}/checklist", tags=["Crew"])
async def get_job_checklist(
    job_id: str,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    crew = db.query(Crew).filter(Crew.email == current_user.get("sub")).first()
    if not crew:
        raise HTTPException(status_code=403, detail="Crew access required")
    
    job = db.query(Job).filter(Job.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    
    if job.assigned_crew_id != crew.id:
        raise HTTPException(status_code=403, detail="This job is not assigned to you")
    
    from app.models.checklist import JobChecklist
    checklist = db.query(JobChecklist).filter(JobChecklist.job_id == job_id).first()
    
    if not checklist:
        raise HTTPException(status_code=404, detail="Checklist not found")
    
    return {
        "job_id": job_id,
        "access_gained_successfully": checklist.access_gained_successfully,
        "waste_verified_with_client": checklist.waste_verified_with_client,
        "no_hazardous_material_found": checklist.no_hazardous_material_found,
        "property_protected": checklist.property_protected,
        "loading_started_safely": checklist.loading_started_safely,
        "completed_at": checklist.completed_at
    }

@router.patch("/crew/jobs/{job_id}/checklist", tags=["Crew"])
async def update_job_checklist(
    job_id: str,
    access_gained_successfully: bool = Form(False),
    waste_verified_with_client: bool = Form(False),
    no_hazardous_material_found: bool = Form(False),
    property_protected: bool = Form(False),
    loading_started_safely: bool = Form(False),
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    crew = db.query(Crew).filter(Crew.email == current_user.get("sub")).first()
    if not crew:
        raise HTTPException(status_code=403, detail="Crew access required")
    
    job = db.query(Job).filter(Job.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    
    if job.assigned_crew_id != crew.id:
        raise HTTPException(status_code=403, detail="This job is not assigned to you")
    
    from app.models.checklist import JobChecklist
    from datetime import datetime
    
    checklist = db.query(JobChecklist).filter(JobChecklist.job_id == job_id).first()
    if not checklist:
        raise HTTPException(status_code=404, detail="Checklist not found")
    
    checklist.access_gained_successfully = access_gained_successfully
    checklist.waste_verified_with_client = waste_verified_with_client
    checklist.no_hazardous_material_found = no_hazardous_material_found
    checklist.property_protected = property_protected
    checklist.loading_started_safely = loading_started_safely
    
    # Mark as completed if all items checked
    if all([access_gained_successfully, waste_verified_with_client, no_hazardous_material_found, 
            property_protected, loading_started_safely]):
        checklist.completed_at = datetime.utcnow()
    
    db.commit()
    
    return {"message": "Checklist updated successfully", "completed_at": checklist.completed_at}

@router.post("/crew/jobs/{job_id}/upload-after-photo", tags=["Crew"])
async def upload_after_photo(
    job_id: str,
    photos: List[UploadFile] = File(default=[]),
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    crew = db.query(Crew).filter(Crew.email == current_user.get("sub")).first()
    if not crew:
        raise HTTPException(status_code=403, detail="Crew access required")
    
    job = db.query(Job).filter(Job.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    
    if job.assigned_crew_id != crew.id:
        raise HTTPException(status_code=403, detail="This job is not assigned to you")
    
    if job.status != "before_photo":
        raise HTTPException(status_code=400, detail=f"Job must be in before_photo status. Current status: {job.status}")
    
    # Check if checklist is completed
    from app.models.checklist import JobChecklist
    checklist = db.query(JobChecklist).filter(JobChecklist.job_id == job_id).first()
    if not checklist or not checklist.completed_at:
        raise HTTPException(status_code=400, detail="Checklist must be completed before uploading after photos")
    
    from app.models.photo import JobPhoto
    uploaded_files = []
    for photo in photos:
        if photo.filename:
            photo_url = storage.upload_job_photo(photo.file, job_id, "after", photo.filename)
            if photo_url:
                uploaded_files.append(photo_url)
                job_photo = JobPhoto(
                    job_id=job_id,
                    photo_url=photo_url,
                    type="after"
                )
                db.add(job_photo)
    
    job.status = "after_photo"
    db.commit()
    return {"message": "After photos uploaded", "status": job.status, "uploaded_count": len(uploaded_files)}

@router.patch("/crew/jobs/{job_id}/complete-work", tags=["Crew"])
async def complete_work(
    job_id: str,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    crew = db.query(Crew).filter(Crew.email == current_user.get("sub")).first()
    if not crew:
        raise HTTPException(status_code=403, detail="Crew access required")
    
    job = db.query(Job).filter(Job.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    
    if job.assigned_crew_id != crew.id:
        raise HTTPException(status_code=403, detail="This job is not assigned to you")
    
    if job.status != "after_photo":
        raise HTTPException(status_code=400, detail="Job must be in after_photo status")
    
    # Count photos
    from app.models.photo import JobPhoto
    before_photos_count = db.query(JobPhoto).filter(
        JobPhoto.job_id == job_id,
        JobPhoto.type == "before"
    ).count()
    
    after_photos_count = db.query(JobPhoto).filter(
        JobPhoto.job_id == job_id,
        JobPhoto.type == "after"
    ).count()
    
    job.status = "work_completed"
    crew.status = "available"
    db.commit()
    
    return {
        "message": "Work completed successfully",
        "job_reference": f"PROP-{job.created_at.year}-{str(job.id)[:3].upper()}-EMERG" if job.created_at else f"PROP-{str(job.id)[:8].upper()}",
        "before_photos": before_photos_count,
        "after_photos": after_photos_count,
        "next_step": "Awaiting admin review",
        "status": job.status
    }

@router.get("/crew/ratings", tags=["Crew"])
async def get_crew_ratings(
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    crew = db.query(Crew).filter(Crew.email == current_user.get("sub")).first()
    if not crew:
        raise HTTPException(status_code=403, detail="Crew access required")
    
    from sqlalchemy import text, func
    
    # Get all completed jobs with ratings
    rated_jobs = db.query(Job).filter(
        Job.assigned_crew_id == crew.id,
        Job.status == "job_completed",
        Job.rating.isnot(None)
    ).all()
    
    # Calculate statistics
    total_jobs = db.query(func.count(Job.id)).filter(
        Job.assigned_crew_id == crew.id,
        Job.status == "job_completed"
    ).scalar()
    
    avg_rating = db.query(func.avg(Job.rating)).filter(
        Job.assigned_crew_id == crew.id,
        Job.status == "job_completed",
        Job.rating.isnot(None)
    ).scalar()
    
    ratings_list = []
    for job in rated_jobs:
        ratings_list.append({
            "job_id": job.id,
            "property_address": job.property_address,
            "rating": job.rating,
            "completed_date": job.updated_at.strftime("%d/%m/%Y, %H:%M:%S") if job.updated_at else None
        })
    
    return {
        "crew_id": crew.id,
        "crew_name": crew.full_name,
        "total_completed_jobs": total_jobs or 0,
        "total_rated_jobs": len(rated_jobs),
        "average_rating": round(float(avg_rating), 2) if avg_rating else 0,
        "ratings": ratings_list
    }


