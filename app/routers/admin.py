from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database.db import get_db
from app.models.crew import Admin, Crew
from app.models.job import Job
from app.models.photo import JobPhoto
from app.core.security import get_current_user
from sqlalchemy import text
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

router = APIRouter()

class ActiveJobResponse(BaseModel):
    job_id: str
    client: str
    property: str
    crew: str
    status: str
    action: str

class PendingCrewResponse(BaseModel):
    id: str
    full_name: str
    email: str
    phone_number: str
    created_at: str

class PendingCrewDetailResponse(BaseModel):
    id: str
    full_name: str
    email: str
    phone_number: str
    address: str
    role: str
    applied: str

class DashboardResponse(BaseModel):
    total: int
    jobs: List[ActiveJobResponse]

class QuoteResponse(BaseModel):
    quote_id: str
    job_id: str
    client: str
    property_address: str
    service_type: str
    urgency_level: str
    sla_hours: str
    van_loads: str
    preferred_date: str
    deposit_price: float
    additional_information: str
    status: str
    property_photos: str
    created_at: str

class SendQuoteRequest(BaseModel):
    quote_amount: float
    deposit_amount: float
    quote_notes: Optional[str] = None

class AvailableCrewResponse(BaseModel):
    id: str
    full_name: str
    phone_number: str
    status: str
    total_jobs: int

class UnassignedJobResponse(BaseModel):
    job_id: str
    property_address: str
    service_type: str
    sla_hours: str
    status: str

class ActiveJobDetailResponse(BaseModel):
    job_id: str
    client: str
    property_address: str
    service_type: str
    urgency_level: str
    sla_hours: str
    van_loads: str
    preferred_date: str
    preferred_time: str
    property_photos: str
    crew: str
    status: str
    action: str

class JobPhotoResponse(BaseModel):
    id: str
    photo_url: str
    type: str
    timestamp: str

class JobVerificationDetailResponse(BaseModel):
    job_id: str
    client_name: str
    property_address: str
    service_type: str
    scheduled_date: str
    crew_name: str
    completed_at: str
    work_duration: str
    sla_status: str
    before_photos: List[JobPhotoResponse]
    after_photos: List[JobPhotoResponse]
    total_photos: int

class JobVerificationListResponse(BaseModel):
    job_id: str
    client_name: str
    property_address: str
    crew_name: str
    scheduled_date: str
    estimated_value: float
    status: str
    photos_count: int

class ApproveJobRequest(BaseModel):
    pass

class SendFinalPriceRequest(BaseModel):
    remaining_amount: float



@router.get("/admin/dashboard/active-jobs", response_model=List[ActiveJobResponse], tags=["Admin"])
async def get_active_jobs_dashboard(
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    admin = db.query(Admin).filter(Admin.email == current_user.get("sub")).first()
    if not admin:
        raise HTTPException(status_code=403, detail="Admin access required")
    
    # Get all jobs that are not completed or cancelled
    jobs = db.query(Job).filter(
        Job.status.notin_(["job_completed", "cancelled"])
    ).order_by(Job.created_at.desc()).all()
    
    result = []
    for job in jobs:
        # Get client info from client backend database
        client_name = "Client"
        try:
            client_result = db.execute(
                text("SELECT full_name FROM clients WHERE id::text = :id"),
                {"id": job.client_id}
            ).fetchone()
            if client_result:
                client_name = client_result[0]
        except:
            pass
        
        # Get assigned crew names
        crew_names = "Not assigned"
        if job.assigned_crew_id:
            crew = db.query(Crew).filter(Crew.id == job.assigned_crew_id).first()
            if crew:
                crew_names = crew.full_name
        
        # Determine status and action based on job workflow
        if job.status == "job_created" and not job.assigned_crew_id:
            # New request needs quote
            status_display = "Needs Quote"
            action = "Create Quote"
        elif job.status == "quote_sent":
            # Quote sent, waiting for client approval
            status_display = "Quote Sent"
            action = "No action needed"
        elif job.status == "quote_accepted":
            # Ready to assign crew
            status_display = "Quote Accepted"
            action = "Assign Crew"
        elif job.status == "crew_assigned":
            # Crew assigned
            status_display = "Crew Assigned"
            action = "No action needed"
        elif job.status in ["crew_arrived", "before_photo", "clearance_in_progress", "after_photo"]:
            # Crew working on site
            status_display = "Work In Progress"
            action = "No action needed"
        elif job.status == "work_completed":
            # Work done, needs final price
            status_display = "Work Done - Set Price"
            action = "Set Final Price"
        else:
            status_display = job.status
            action = "Review"
        
        result.append({
            "job_id": job.id,
            "client": client_name,
            "property": job.property_address,
            "crew": crew_names,
            "status": status_display,
            "action": action
        })
    
    return result

@router.get("/admin/crew/pending", response_model=List[PendingCrewResponse], tags=["Admin"], summary="Get All Pending User Approvals")
async def get_pending_crew(
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    admin = db.query(Admin).filter(Admin.email == current_user.get("sub")).first()
    if not admin:
        raise HTTPException(status_code=403, detail="Admin access required")
    
    pending_crew = db.query(Crew).filter(Crew.is_approved == False).all()
    
    return [
        {
            "id": crew.id,
            "full_name": crew.full_name,
            "email": crew.email,
            "phone_number": crew.phone_number or "",
            "created_at": crew.created_at.isoformat() if crew.created_at else ""
        }
        for crew in pending_crew
    ]

@router.get("/admin/crew/pending/{crew_id}", response_model=PendingCrewDetailResponse, tags=["Admin"])
async def get_pending_crew_by_id(
    crew_id: str,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    admin = db.query(Admin).filter(Admin.email == current_user.get("sub")).first()
    if not admin:
        raise HTTPException(status_code=403, detail="Admin access required")
    
    crew = db.query(Crew).filter(Crew.id == crew_id, Crew.is_approved == False).first()
    if not crew:
        raise HTTPException(status_code=404, detail="Pending crew not found")
    
    return {
        "id": crew.id,
        "full_name": crew.full_name,
        "email": crew.email,
        "phone_number": crew.phone_number or "",
        "address": admin.business_address if admin.business_address else "",
        "role": "Crew",
        "applied": crew.created_at.strftime("%m/%d/%Y") if crew.created_at else ""
    }

@router.put("/admin/crew/{crew_id}/approve", tags=["Admin"])
async def approve_crew(
    crew_id: str,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    admin = db.query(Admin).filter(Admin.email == current_user.get("sub")).first()
    if not admin:
        raise HTTPException(status_code=403, detail="Admin access required")
    
    crew = db.query(Crew).filter(Crew.id == crew_id).first()
    if not crew:
        raise HTTPException(status_code=404, detail="Crew not found")
    
    crew.is_approved = True
    db.commit()
    
    return {"message": f"Crew {crew.full_name} approved successfully"}

@router.delete("/admin/crew/{crew_id}/reject", tags=["Admin"])
async def reject_crew(
    crew_id: str,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    admin = db.query(Admin).filter(Admin.email == current_user.get("sub")).first()
    if not admin:
        raise HTTPException(status_code=403, detail="Admin access required")
    
    crew = db.query(Crew).filter(Crew.id == crew_id).first()
    if not crew:
        raise HTTPException(status_code=404, detail="Crew not found")
    
    db.delete(crew)
    db.commit()
    
    return {"message": f"Crew {crew.full_name} rejected and removed"}

@router.get("/admin/quotes", response_model=List[QuoteResponse], tags=["Admin"], summary="Get All Quotes Created")
async def get_all_quotes(
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    admin = db.query(Admin).filter(Admin.email == current_user.get("sub")).first()
    if not admin:
        raise HTTPException(status_code=403, detail="Admin access required")
    
    # Get all jobs - only job_created status (awaiting quotes)
    jobs = db.query(Job).filter(
        Job.status == "job_created"
    ).order_by(Job.created_at.desc()).all()
    
    result = []
    for job in jobs:
        client_name = "Client"
        try:
            client_result = db.execute(
                text("SELECT full_name FROM clients WHERE id = :id"),
                {"id": job.client_id}
            ).fetchone()
            if client_result:
                client_name = client_result[0]
        except:
            pass
        
        # Get service type name
        service_type_name = job.service_type
        try:
            service_result = db.execute(
                text("SELECT name FROM service_types WHERE id = :id"),
                {"id": job.service_type}
            ).fetchone()
            if service_result:
                service_type_name = service_result[0]
        except:
            pass
        
        # Get urgency level name and SLA hours
        urgency_name = ""
        sla_hours = ""
        if job.urgency_level:
            try:
                urgency_result = db.execute(
                    text("SELECT name, sla_hours FROM urgency_levels WHERE id = :id"),
                    {"id": job.urgency_level}
                ).fetchone()
                if urgency_result:
                    urgency_name = urgency_result[0]
                    sla_hours = f"{urgency_result[1]}hr"
            except:
                pass
        
        result.append({
            "quote_id": job.id,
            "job_id": job.id,
            "client": client_name,
            "property_address": job.property_address,
            "service_type": service_type_name,
            "urgency_level": urgency_name,
            "sla_hours": sla_hours,
            "van_loads": str(job.van_loads) if job.van_loads else "",
            "preferred_date": job.preferred_date if job.preferred_date else "",
            "deposit_price": job.deposit_amount if job.deposit_amount else 0.0,
            "additional_information": job.additional_information if job.additional_information else "",
            "status": job.status,
            "property_photos": job.property_photos if job.property_photos else "",
            "created_at": job.created_at.isoformat() if job.created_at else ""
        })
    
    return result

@router.get("/admin/quotes/sent", tags=["Admin"], summary="Get All Sent Quotes Awaiting Client Response")
async def get_sent_quotes(
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    admin = db.query(Admin).filter(Admin.email == current_user.get("sub")).first()
    if not admin:
        raise HTTPException(status_code=403, detail="Admin access required")
    
    # Get all jobs with quote_sent status
    jobs = db.query(Job).filter(
        Job.status == "quote_sent"
    ).order_by(Job.created_at.desc()).all()
    
    result = []
    for job in jobs:
        client_name = "Client"
        try:
            client_result = db.execute(
                text("SELECT company_name FROM clients WHERE id = :id"),
                {"id": job.client_id}
            ).fetchone()
            if client_result:
                client_name = client_result[0]
        except:
            pass
        
        # Calculate remaining amount
        total_amount = job.quote_amount if job.quote_amount else 0.0
        deposit_amount = job.deposit_amount if job.deposit_amount else 0.0
        remaining_amount = total_amount - deposit_amount
        
        # Get admin who sent the quote
        quoted_by = "Admin"
        if job.assigned_by:
            admin_user = db.query(Admin).filter(Admin.id == job.assigned_by).first()
            if admin_user:
                quoted_by = admin_user.full_name if hasattr(admin_user, 'full_name') else "Admin"
        
        # Calculate valid until (24 hours from sent time)
        from datetime import timedelta
        valid_until = ""
        if job.updated_at:
            valid_until_date = job.updated_at + timedelta(hours=24)
            valid_until = valid_until_date.strftime("%m/%d/%Y")
        
        result.append({
            "job_id": job.id,
            "client": client_name,
            "total_amount": total_amount,
            "deposit_amount": deposit_amount,
            "remaining_amount": remaining_amount,
            "quote_notes": job.quote_notes if job.quote_notes else "",
            "quoted_by": quoted_by,
            "sent_on": job.updated_at.isoformat() if job.updated_at else "",
            "valid_until": valid_until,
            "status": "QUOTE SENT"
        })
    
    return result

@router.get("/admin/quotes/accepted", tags=["Admin"], summary="Get All Accepted Quotes")
async def get_accepted_quotes(
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    admin = db.query(Admin).filter(Admin.email == current_user.get("sub")).first()
    if not admin:
        raise HTTPException(status_code=403, detail="Admin access required")
    
    # Get all jobs (for debugging)
    all_jobs = db.query(Job).all()
    print(f"Total jobs in database: {len(all_jobs)}")
    for j in all_jobs:
        print(f"Job {j.id}: status={j.status}")
    
    # Get all jobs that are accepted (including verified jobs awaiting final payment)
    jobs = db.query(Job).filter(
        Job.status.in_(["quote_accepted", "deposit_paid", "crew_assigned", "crew_arrived", "before_photo", "clearance_in_progress", "after_photo", "work_completed", "job_verified", "payment_pending"])
    ).order_by(Job.updated_at.desc()).all()
    
    print(f"Filtered accepted jobs: {len(jobs)}")
    
    result = []
    for job in jobs:
        client_name = "Client"
        client_email = ""
        try:
            client_result = db.execute(
                text("SELECT full_name, email FROM clients WHERE id = :id"),
                {"id": job.client_id}
            ).fetchone()
            if client_result:
                client_name = client_result[0]
                client_email = client_result[1] if len(client_result) > 1 else ""
        except:
            pass
        
        total_amount = job.quote_amount if job.quote_amount else 0.0
        deposit_amount = job.deposit_amount if job.deposit_amount else 0.0
        remaining_amount = total_amount - deposit_amount
        
        # Check actual payment status
        payment_status = "Pending"
        paid_on = ""
        deposit_paid_amount = 0.0
        try:
            payment_result = db.execute(
                text("SELECT payment_status, paid_at FROM payments WHERE job_id = :job_id AND payment_type = 'deposit' AND payment_status = 'succeeded'"),
                {"job_id": job.id}
            ).fetchone()
            if payment_result:
                payment_status = "Paid"
                paid_on = payment_result[1].isoformat() if payment_result[1] else ""
                deposit_paid_amount = deposit_amount
        except:
            pass
        
        quoted_by = "Admin"
        if job.assigned_by:
            admin_user = db.query(Admin).filter(Admin.id == job.assigned_by).first()
            if admin_user:
                quoted_by = admin_user.full_name if hasattr(admin_user, 'full_name') else "Admin"
        
        quoted_on = job.created_at.isoformat() if job.created_at else ""
        accepted_on = job.updated_at.isoformat() if job.updated_at else ""
        
        result.append({
            "job_id": job.id,
            "client": client_name,
            "client_email": client_email,
            "total_amount": total_amount,
            "deposit_amount": deposit_amount,
            "remaining_amount": remaining_amount,
            "quote_notes": job.quote_notes if job.quote_notes else "",
            "quoted_by": quoted_by,
            "quoted_on": quoted_on,
            "accepted_on": accepted_on,
            "deposit_paid": deposit_paid_amount,
            "payment_status": payment_status,
            "paid_on": paid_on,
            "status": "BOOKING CONFIRMED"
        })
    
    return result

@router.post("/admin/quotes/{job_id}/send", tags=["Admin"], summary="Send Quote to Client")
async def send_quote(
    job_id: str,
    quote_data: SendQuoteRequest,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    admin = db.query(Admin).filter(Admin.email == current_user.get("sub")).first()
    if not admin:
        raise HTTPException(status_code=403, detail="Admin access required")
    
    job = db.query(Job).filter(Job.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    
    if job.status != "job_created":
        raise HTTPException(status_code=400, detail="Quote already sent for this job")
    
    job.quote_amount = quote_data.quote_amount
    job.deposit_amount = quote_data.deposit_amount
    job.quote_notes = quote_data.quote_notes
    job.status = "quote_sent"
    
    db.commit()
    
    return {
        "message": "Quote sent successfully",
        "job_id": job.id,
        "quote_amount": job.quote_amount,
        "deposit_amount": job.deposit_amount,
        "status": job.status
    }

@router.get("/admin/crew/available", response_model=List[AvailableCrewResponse], tags=["Admin"], summary="Get Available Crew Members")
async def get_available_crew(
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    admin = db.query(Admin).filter(Admin.email == current_user.get("sub")).first()
    if not admin:
        raise HTTPException(status_code=403, detail="Admin access required")
    
    crew_members = db.query(Crew).filter(
        Crew.is_approved == True,
        Crew.status == "available"
    ).all()
    
    result = []
    for crew in crew_members:
        total_jobs = db.query(Job).filter(Job.assigned_crew_id == crew.id).count()
        
        result.append({
            "id": crew.id,
            "full_name": crew.full_name,
            "phone_number": crew.phone_number if crew.phone_number else "",
            "status": crew.status,
            "total_jobs": total_jobs
        })
    
    return result

@router.post("/admin/jobs/{job_id}/assign-crew/{crew_id}", tags=["Admin"], summary="Assign Crew to Job")
async def assign_crew_to_job(
    job_id: str,
    crew_id: str,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    admin = db.query(Admin).filter(Admin.email == current_user.get("sub")).first()
    if not admin:
        raise HTTPException(status_code=403, detail="Admin access required")
    
    job = db.query(Job).filter(Job.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    
    if job.status not in ["quote_accepted", "deposit_paid"]:
        raise HTTPException(status_code=400, detail="Job must be in quote_accepted or deposit_paid status to assign crew")
    
    crew = db.query(Crew).filter(Crew.id == crew_id, Crew.is_approved == True).first()
    if not crew:
        raise HTTPException(status_code=404, detail="Approved crew not found")
    
    job.assigned_crew_id = crew_id
    job.assigned_by = admin.id
    job.status = "crew_assigned"
    crew.status = "assigned"
    
    db.commit()
    
    return {
        "message": "Crew assigned successfully",
        "job_id": job.id,
        "crew_id": crew.id,
        "crew_name": crew.full_name,
        "status": job.status
    }

@router.get("/admin/jobs/unassigned/{job_id}", tags=["Admin"], summary="Get Unassigned Job Details by ID")
async def get_unassigned_job_by_id(
    job_id: str,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    admin = db.query(Admin).filter(Admin.email == current_user.get("sub")).first()
    if not admin:
        raise HTTPException(status_code=403, detail="Admin access required")
    
    job = db.query(Job).filter(Job.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    
    if job.status not in ["quote_accepted", "deposit_paid"] or job.assigned_crew_id is not None:
        raise HTTPException(status_code=400, detail="Job is not unassigned")
    
    client_name = "Client"
    try:
        client_result = db.execute(
            text("SELECT company_name FROM clients WHERE id = :id"),
            {"id": job.client_id}
        ).fetchone()
        if client_result:
            client_name = client_result[0]
    except:
        pass
    
    service_type_name = job.service_type
    try:
        service_result = db.execute(
            text("SELECT name FROM service_types WHERE id = :id"),
            {"id": job.service_type}
        ).fetchone()
        if service_result:
            service_type_name = service_result[0]
    except:
        pass
    
    urgency_name = ""
    sla_hours = ""
    if job.urgency_level:
        try:
            urgency_result = db.execute(
                text("SELECT name, sla_hours FROM urgency_levels WHERE id = :id"),
                {"id": job.urgency_level}
            ).fetchone()
            if urgency_result:
                urgency_name = urgency_result[0]
                sla_hours = f"{urgency_result[1]}hr"
        except:
            pass
    
    # Get available crew
    crew_members = db.query(Crew).filter(
        Crew.is_approved == True,
        Crew.status == "available"
    ).all()
    
    available_crew = []
    for crew in crew_members:
        total_jobs = db.query(Job).filter(
            Job.assigned_crew_id == crew.id,
            Job.status == "job_completed"
        ).count()
        
        available_crew.append({
            "id": crew.id,
            "full_name": crew.full_name,
            "phone_number": crew.phone_number if crew.phone_number else "",
            "status": crew.status,
            "total_jobs": total_jobs
        })
    
    return {
        "job_id": job.id,
        "property_address": job.property_address,
        "service_type": service_type_name,
        "sla_hours": sla_hours,
        "available_crew": available_crew
    }

@router.get("/admin/jobs/unassigned", response_model=List[UnassignedJobResponse], tags=["Admin"], summary="Get Unassigned Jobs")
async def get_unassigned_jobs(
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    admin = db.query(Admin).filter(Admin.email == current_user.get("sub")).first()
    if not admin:
        raise HTTPException(status_code=403, detail="Admin access required")
    
    jobs = db.query(Job).filter(
        Job.status.in_(["quote_accepted", "deposit_paid"]),
        Job.assigned_crew_id.is_(None)
    ).order_by(Job.created_at.desc()).all()
    
    result = []
    for job in jobs:
        # Get service type name
        service_type_name = job.service_type
        try:
            service_result = db.execute(
                text("SELECT name FROM service_types WHERE id = :id"),
                {"id": job.service_type}
            ).fetchone()
            if service_result:
                service_type_name = service_result[0]
        except:
            pass
        
        # Get SLA hours from urgency level
        sla_hours = ""
        if job.urgency_level:
            try:
                urgency_result = db.execute(
                    text("SELECT sla_hours FROM urgency_levels WHERE id = :id"),
                    {"id": job.urgency_level}
                ).fetchone()
                if urgency_result:
                    sla_hours = f"{urgency_result[0]}hr"
            except:
                pass
        
        result.append({
            "job_id": job.id,
            "property_address": job.property_address,
            "service_type": service_type_name,
            "sla_hours": sla_hours,
            "status": "Needs Crew"
        })
    
    return result

@router.get("/admin/jobs/{job_id}/available-crew", response_model=List[AvailableCrewResponse], tags=["Admin"], summary="Get Available Crew for Job")
async def get_available_crew_for_job(
    job_id: str,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    admin = db.query(Admin).filter(Admin.email == current_user.get("sub")).first()
    if not admin:
        raise HTTPException(status_code=403, detail="Admin access required")
    
    job = db.query(Job).filter(Job.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    
    crew_members = db.query(Crew).filter(
        Crew.is_approved == True,
        Crew.status == "available"
    ).all()
    
    result = []
    for crew in crew_members:
        total_jobs = db.query(Job).filter(
            Job.assigned_crew_id == crew.id,
            Job.status == "job_completed"
        ).count()
        
        result.append({
            "id": crew.id,
            "full_name": crew.full_name,
            "phone_number": crew.phone_number if crew.phone_number else "",
            "status": crew.status,
            "total_jobs": total_jobs
        })
    
    return result

# ============ JOB VERIFICATION ENDPOINTS ============

@router.get("/admin/verification/jobs", response_model=List[JobVerificationListResponse], tags=["Admin"], summary="Get All Jobs Pending Verification")
async def get_jobs_pending_verification(
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    admin = db.query(Admin).filter(Admin.email == current_user.get("sub")).first()
    if not admin:
        raise HTTPException(status_code=403, detail="Admin access required")
    
    jobs = db.query(Job).filter(Job.status == "work_completed").order_by(Job.updated_at.desc()).all()
    
    result = []
    for job in jobs:
        client_name = "Unknown Client"
        try:
            client_result = db.execute(
                text("SELECT company_name FROM clients WHERE id = :id"),
                {"id": job.client_id}
            ).fetchone()
            if client_result:
                client_name = client_result[0]
        except:
            pass
        
        crew_name = "Unknown Crew"
        if job.assigned_crew_id:
            crew = db.query(Crew).filter(Crew.id == job.assigned_crew_id).first()
            if crew:
                crew_name = crew.full_name
        
        photos_count = db.query(JobPhoto).filter(JobPhoto.job_id == job.id).count()
        
        result.append({
            "job_id": job.id,
            "client_name": client_name,
            "property_address": job.property_address,
            "crew_name": crew_name,
            "scheduled_date": job.preferred_date if job.preferred_date else "",
            "estimated_value": job.quote_amount if job.quote_amount else 0.0,
            "status": "Ready to Verify",
            "photos_count": photos_count
        })
    
    return result

@router.get("/admin/verification/jobs/{job_id}", response_model=JobVerificationDetailResponse, tags=["Admin"], summary="Get Job Verification Details")
async def get_job_verification_details(
    job_id: str,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    admin = db.query(Admin).filter(Admin.email == current_user.get("sub")).first()
    if not admin:
        raise HTTPException(status_code=403, detail="Admin access required")
    
    job = db.query(Job).filter(Job.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    
    if job.status != "work_completed":
        raise HTTPException(status_code=400, detail="Job is not pending verification")
    
    client_name = "Unknown Client"
    try:
        client_result = db.execute(
            text("SELECT company_name FROM clients WHERE id = :id"),
            {"id": job.client_id}
        ).fetchone()
        if client_result:
            client_name = client_result[0]
    except:
        pass
    
    crew_name = "Unknown Crew"
    crew_id = ""
    if job.assigned_crew_id:
        crew = db.query(Crew).filter(Crew.id == job.assigned_crew_id).first()
        if crew:
            crew_name = crew.full_name
            crew_id = crew.id
    
    service_type_name = job.service_type
    try:
        service_result = db.execute(
            text("SELECT name FROM service_types WHERE id = :id"),
            {"id": job.service_type}
        ).fetchone()
        if service_result:
            service_type_name = service_result[0]
    except:
        pass
    
    before_photos = db.query(JobPhoto).filter(
        JobPhoto.job_id == job_id,
        JobPhoto.type == "before"
    ).all()
    
    after_photos = db.query(JobPhoto).filter(
        JobPhoto.job_id == job_id,
        JobPhoto.type == "after"
    ).all()
    
    # Calculate work duration and SLA status
    work_duration = "N/A"
    sla_status = "SLA Met"
    if job.created_at and job.updated_at:
        duration = job.updated_at - job.created_at
        hours = int(duration.total_seconds() // 3600)
        minutes = int((duration.total_seconds() % 3600) // 60)
        if hours > 0:
            work_duration = f"{hours}h {minutes}m"
        else:
            work_duration = f"{minutes}m"
    
    return {
        "job_id": job.id,
        "client_name": client_name,
        "property_address": job.property_address,
        "service_type": service_type_name,
        "scheduled_date": job.preferred_date if job.preferred_date else "",
        "crew_name": crew_name,
        "completed_at": job.updated_at.isoformat() if job.updated_at else "",
        "work_duration": work_duration,
        "sla_status": sla_status,
        "before_photos": [
            {
                "id": photo.id,
                "photo_url": photo.photo_url,
                "type": photo.type,
                "timestamp": photo.timestamp.isoformat() if photo.timestamp else ""
            }
            for photo in before_photos
        ],
        "after_photos": [
            {
                "id": photo.id,
                "photo_url": photo.photo_url,
                "type": photo.type,
                "timestamp": photo.timestamp.isoformat() if photo.timestamp else ""
            }
            for photo in after_photos
        ],
        "total_photos": len(before_photos) + len(after_photos)
    }

@router.post("/admin/verification/jobs/{job_id}/approve", tags=["Admin"], summary="Approve Job and Complete Verification")
async def approve_job_verification(
    job_id: str,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    admin = db.query(Admin).filter(Admin.email == current_user.get("sub")).first()
    if not admin:
        raise HTTPException(status_code=403, detail="Admin access required")
    
    job = db.query(Job).filter(Job.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    
    if job.status != "work_completed":
        raise HTTPException(status_code=400, detail="Job is not pending verification")
    
    job.status = "job_verified"
    
    if job.assigned_crew_id:
        crew = db.query(Crew).filter(Crew.id == job.assigned_crew_id).first()
        if crew:
            crew.status = "available"
    
    db.commit()
    
    return {
        "message": "Job verified successfully",
        "job_id": job.id,
        "status": job.status
    }

@router.post("/admin/verification/jobs/{job_id}/reject", tags=["Admin"], summary="Reject Job Verification")
async def reject_job_verification(
    job_id: str,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    admin = db.query(Admin).filter(Admin.email == current_user.get("sub")).first()
    if not admin:
        raise HTTPException(status_code=403, detail="Admin access required")
    
    job = db.query(Job).filter(Job.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    
    if job.status != "work_completed":
        raise HTTPException(status_code=400, detail="Job is not pending verification")
    
    job.status = "clearance_in_progress"
    
    db.commit()
    
    return {
        "message": "Job verification rejected. Crew needs to resubmit.",
        "job_id": job.id,
        "status": job.status
    }

@router.post("/admin/verification/jobs/{job_id}/send-payment-request", tags=["Admin"], summary="Send Final Price and Payment Request")
async def send_payment_request(
    job_id: str,
    request: SendFinalPriceRequest,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    admin = db.query(Admin).filter(Admin.email == current_user.get("sub")).first()
    if not admin:
        raise HTTPException(status_code=403, detail="Admin access required")
    
    job = db.query(Job).filter(Job.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    
    if job.status != "job_verified":
        raise HTTPException(status_code=400, detail="Job must be verified before sending payment request")
    
    deposit_paid = job.deposit_amount if job.deposit_amount else 0.0
    final_price = deposit_paid + request.remaining_amount
    
    job.quote_amount = final_price
    job.remaining_amount = request.remaining_amount
    job.status = "payment_pending"
    
    db.commit()
    
    return {
        "message": "Payment request sent to client successfully",
        "job_id": job.id,
        "final_price": final_price,
        "deposit_paid": deposit_paid,
        "remaining_amount": request.remaining_amount,
        "status": job.status
    }


@router.get("/admin/payments/completed", tags=["Admin"], summary="Get Completed Payments")
async def get_completed_payments(
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all completed payments (fully paid jobs)"""
    admin = db.query(Admin).filter(Admin.email == current_user.get("sub")).first()
    if not admin:
        raise HTTPException(status_code=403, detail="Admin access required")
    
    try:
        query = text("""
            SELECT 
                j.id, j.property_address, j.service_type, j.quote_amount,
                j.deposit_amount, j.remaining_amount, j.updated_at,
                c.company_name, c.email
            FROM jobs j
            LEFT JOIN clients c ON j.client_id::uuid = c.id
            WHERE j.status = 'job_completed'
            ORDER BY j.updated_at DESC
        """)
        results = db.execute(query).fetchall()
        
        payments = []
        for r in results:
            service_type_name = r[2]
            try:
                service_result = db.execute(
                    text("SELECT name FROM service_types WHERE id = :id"),
                    {"id": r[2]}
                ).fetchone()
                if service_result:
                    service_type_name = service_result[0]
            except:
                pass
            
            payments.append({
                "job_id": r[0],
                "client_name": r[7] or "Unknown Client",
                "client_email": r[8] or "",
                "property_address": r[1],
                "service_type": service_type_name,
                "total_amount": float(r[3]) if r[3] else 0.0,
                "deposit_paid": float(r[4]) if r[4] else 0.0,
                "remaining_paid": float(r[5]) if r[5] else 0.0,
                "completed_at": r[6].strftime("%m/%d/%Y") if r[6] else "",
                "status": "Fully Paid"
            })
        
        return payments
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")

@router.get("/admin/payments/pending", tags=["Admin"], summary="Get Pending Payments")
async def get_pending_payments(
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all pending payments (deposit and remaining)"""
    admin = db.query(Admin).filter(Admin.email == current_user.get("sub")).first()
    if not admin:
        raise HTTPException(status_code=403, detail="Admin access required")
    
    try:
        # Get jobs with quote_accepted (deposit pending) OR payment_pending (remaining pending)
        query = text("""
            SELECT 
                j.id, j.property_address, j.service_type, j.quote_amount,
                j.deposit_amount, j.remaining_amount, j.status, c.full_name, c.email
            FROM jobs j
            LEFT JOIN clients c ON j.client_id::uuid = c.id
            WHERE j.status IN ('quote_accepted', 'payment_pending')
            ORDER BY j.created_at DESC
        """)
        results = db.execute(query).fetchall()
        
        payments = []
        for r in results:
            service_type_name = r[2]
            try:
                service_result = db.execute(
                    text("SELECT name FROM service_types WHERE id = :id"),
                    {"id": r[2]}
                ).fetchone()
                if service_result:
                    service_type_name = service_result[0]
            except:
                pass
            
            # Determine payment type and amount
            if r[6] == "quote_accepted":
                payment_type = "Deposit Payment"
                amount_due = float(r[4]) if r[4] else 0.0
            else:  # payment_pending
                payment_type = "Remaining Payment"
                amount_due = float(r[5]) if r[5] else 0.0
            
            payments.append({
                "job_id": r[0],
                "client_name": r[7] or "Unknown Client",
                "client_email": r[8] or "",
                "property_address": r[1],
                "service_type": service_type_name,
                "total_amount": float(r[3]) if r[3] else 0.0,
                "amount_due": amount_due,
                "payment_type": payment_type,
                "status": "Payment Pending"
            })
        
        return payments
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")
