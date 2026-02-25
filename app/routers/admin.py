from fastapi import APIRouter, Depends, HTTPException, Form
from sqlalchemy.orm import Session
from app.database.db import get_db
from app.models.crew import Admin
from app.models.job import Job
from app.models.photo import JobPhoto
from app.core.security import get_current_user
from sqlalchemy import text
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

router = APIRouter()
import re


def resolve_client(db, client_identifier):
    """Return (full_name, phone_number, email) for a given client identifier.
    Tries multiple matching strategies and logs failures for debugging.
    """
    default = ("Client", "", None)
    if not client_identifier:
        return default

    id_raw = str(client_identifier).strip()
    # clean common wrappers
    id_clean = id_raw.strip().strip('"').strip("'").strip('{}')

    # prefer explicit uuid substring if present
    m = re.search(r'([0-9a-fA-F\-]{36})', id_clean)
    candidates = []
    if m:
        candidates.append(m.group(1))
    candidates.append(id_clean)

    for cand in candidates:
        try:
            client_result = db.execute(
                text("SELECT full_name, phone_number, email FROM clients WHERE id::text = :id OR lower(email) = lower(:id) OR phone_number = :id"),
                {"id": cand}
            ).fetchone()
            if client_result:
                full_name = client_result[0] if client_result[0] else "Client"
                phone = client_result[1] if client_result[1] else ""
                email = client_result[2] if len(client_result) > 2 and client_result[2] else None
                return (full_name, phone, email)
        except Exception as e:
            print(f"[resolve_client] query error for candidate={cand}: {e}")

    print(f"[resolve_client] no client found for raw id={id_raw}")
    return default

class ActiveJobResponse(BaseModel):
    job_id: str
    client: str
    client_email: Optional[str] = None
    property_address: str
    crew: Optional[str] = None
    date: Optional[str] = None
    quote_amount: float = 0.0
    waste_types: Optional[List[str]] = None
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
    vehicle_number: str
    profile_photo: str
    drivers_license: str
    dbs_certificate: str
    proof_of_address: str
    insurance_certificate: str
    right_to_work: str
    role: str
    applied: str

class DashboardResponse(BaseModel):
    total: int
    jobs: List[ActiveJobResponse]

class QuoteResponse(BaseModel):
    quote_id: str
    job_id: str
    client: str
    client_email: Optional[str] = None
    client_phone: str
    property_address: str
    urgency_level: str
    waste_types: Optional[List[str]] = None
    van_loads: Optional[str] = None
    preferred_date: str
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
    scheduled_date: str
    estimated_value: float
    status: str
    photos_count: int

class ApproveJobRequest(BaseModel):
    pass

class SendFinalPriceRequest(BaseModel):
    remaining_amount: float



@router.get("/admin/dashboard/active-jobs", response_model=List[ActiveJobResponse], response_model_exclude_none=True, tags=["Admin"])
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
        client_name, client_phone, client_email = resolve_client(db, job.client_id)
        
        # Get assigned crew names (crew table removed/disabled)
        crew_names = "Not assigned"
        if job.assigned_crew_id:
            # avoid querying a missing `crew` table; show assigned status
            crew_names = "Assigned"
        
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
            # Waiting for deposit payment
            status_display = "Awaiting Deposit"
            action = "Wait for Payment"
        elif job.status == "deposit_paid":
            # Ready to assign crew
            status_display = "Deposit Paid"
            action = "Assign Crew"
        elif job.status == "deposit_paid":
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
        
        # Resolve waste type names (if any)
        waste_names = None
        if job.waste_types:
            try:
                import json
                parsed = None
                try:
                    parsed = json.loads(job.waste_types)
                except:
                    parsed = [s.strip() for s in str(job.waste_types).split(',') if s.strip()]

                resolved = []
                for wt in parsed:
                    # try numeric id lookup
                    try:
                        wt_id = int(wt)
                        wt_res = db.execute(text("SELECT name FROM waste_types WHERE id = :id"), {"id": wt_id}).fetchone()
                        if wt_res:
                            resolved.append(wt_res[0])
                        else:
                            resolved.append(str(wt))
                    except Exception:
                        # try lookup by name, else use raw value
                        try:
                            wt_res = db.execute(text("SELECT name FROM waste_types WHERE name = :name"), {"name": wt}).fetchone()
                            if wt_res:
                                resolved.append(wt_res[0])
                            else:
                                resolved.append(str(wt))
                        except:
                            resolved.append(str(wt))

                if resolved:
                    waste_names = resolved
            except:
                waste_names = None

        entry = {
            "job_id": job.id,
            "client": client_name,
            "client_email": client_email,
            "property_address": job.property_address,
            "date": job.preferred_date if job.preferred_date else None,
            "quote_amount": job.quote_amount if job.quote_amount is not None else 0.0,
            "waste_types": waste_names,
            "status": status_display,
            "action": action
        }
        if job.assigned_crew_id:
            entry["crew"] = crew_names

        result.append(entry)
    
    return result








# Removed: crew approval/rejection endpoints
# The endpoints PUT /admin/crew/{crew_id}/approve and DELETE /admin/crew/{crew_id}/reject
# were removed per request. Approval/rejection of crew should be managed elsewhere
# or via an admin UI action that invokes internal workflows. If you want a
# replacement endpoint (e.g., an admin-only batch approval), I can add one.

@router.get("/admin/quotes", response_model=List[QuoteResponse], response_model_exclude_none=True, tags=["Admin"], summary="Get All Quotes Created")
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
        client_name, client_phone, client_email = resolve_client(db, job.client_id)
        
        # service_type removed from response per request
        
        # Get urgency level name
        urgency_name = ""
        if job.urgency_level:
            try:
                urgency_result = db.execute(
                    text("SELECT name FROM urgency_levels WHERE id = :id"),
                    {"id": job.urgency_level}
                ).fetchone()
                if urgency_result:
                    urgency_name = urgency_result[0]
            except:
                pass

        # Resolve waste type names for the quote
        waste_names = None
        if job.waste_types:
            try:
                import json
                parsed = None
                try:
                    parsed = json.loads(job.waste_types)
                except:
                    parsed = [s.strip() for s in str(job.waste_types).split(',') if s.strip()]

                resolved = []
                for wt in parsed:
                    try:
                        wt_id = int(wt)
                        wt_res = db.execute(text("SELECT name FROM waste_types WHERE id = :id"), {"id": wt_id}).fetchone()
                        if wt_res:
                            resolved.append(wt_res[0])
                        else:
                            resolved.append(str(wt))
                    except Exception:
                        try:
                            wt_res = db.execute(text("SELECT name FROM waste_types WHERE name = :name"), {"name": wt}).fetchone()
                            if wt_res:
                                resolved.append(wt_res[0])
                            else:
                                resolved.append(str(wt))
                        except:
                            resolved.append(str(wt))

                if resolved:
                    waste_names = resolved
            except:
                waste_names = None
        
        entry = {
            "quote_id": job.id,
            "job_id": job.id,
            "client": client_name,
            "client_email": client_email,
            "client_phone": client_phone,
            "property_address": job.property_address,
            "urgency_level": urgency_name,
            "preferred_date": job.preferred_date if job.preferred_date else "",
            "additional_information": job.additional_information if job.additional_information else "",
            "status": job.status,
            "property_photos": job.property_photos if job.property_photos else "",
            "created_at": job.created_at.isoformat() if job.created_at else ""
        }
        if job.van_loads is not None:
            entry["van_loads"] = str(job.van_loads)
        if waste_names is not None:
            entry["waste_types"] = waste_names

        result.append(entry)
    
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
        client_name, client_phone, client_email = resolve_client(db, job.client_id)

        # Resolve waste type names for the sent quote
        waste_names = None
        if job.waste_types:
            try:
                import json
                parsed = None
                try:
                    parsed = json.loads(job.waste_types)
                except:
                    parsed = [s.strip() for s in str(job.waste_types).split(',') if s.strip()]

                resolved = []
                for wt in parsed:
                    try:
                        wt_id = int(wt)
                        wt_res = db.execute(text("SELECT name FROM waste_types WHERE id = :id"), {"id": wt_id}).fetchone()
                        if wt_res:
                            resolved.append(wt_res[0])
                        else:
                            resolved.append(str(wt))
                    except Exception:
                        try:
                            wt_res = db.execute(text("SELECT name FROM waste_types WHERE name = :name"), {"name": wt}).fetchone()
                            if wt_res:
                                resolved.append(wt_res[0])
                            else:
                                resolved.append(str(wt))
                        except:
                            resolved.append(str(wt))

                if resolved:
                    waste_names = resolved
            except:
                waste_names = None

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

        entry = {
            "job_id": job.id,
            "client": client_name,
            "client_email": client_email,
            "client_phone": client_phone,
            "property_address": job.property_address,
            "total_amount": total_amount,
            "deposit_amount": deposit_amount,
            "remaining_amount": remaining_amount,
            "quote_notes": job.quote_notes if job.quote_notes else "",
            "sent_on": job.updated_at.isoformat() if job.updated_at else "",
            "valid_until": valid_until,
            "status": "QUOTE SENT",
            "property_photos": job.property_photos if job.property_photos else "",
            "additional_information": job.additional_information if job.additional_information else "",
            "preferred_date": job.preferred_date if job.preferred_date else ""
        }
        if waste_names is not None:
            entry["waste_types"] = waste_names
        result.append(entry)
    
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
        client_name, client_phone, client_email = resolve_client(db, job.client_id)
        
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
        
        # Resolve waste type names for the accepted quote
        waste_names = None
        if job.waste_types:
            try:
                import json
                parsed = None
                try:
                    parsed = json.loads(job.waste_types)
                except:
                    parsed = [s.strip() for s in str(job.waste_types).split(',') if s.strip()]

                resolved = []
                for wt in parsed:
                    try:
                        wt_id = int(wt)
                        wt_res = db.execute(text("SELECT name FROM waste_types WHERE id = :id"), {"id": wt_id}).fetchone()
                        if wt_res:
                            resolved.append(wt_res[0])
                        else:
                            resolved.append(str(wt))
                    except Exception:
                        try:
                            wt_res = db.execute(text("SELECT name FROM waste_types WHERE name = :name"), {"name": wt}).fetchone()
                            if wt_res:
                                resolved.append(wt_res[0])
                            else:
                                resolved.append(str(wt))
                        except:
                            resolved.append(str(wt))

                if resolved:
                    waste_names = resolved
            except:
                waste_names = None

        quoted_on = job.created_at.isoformat() if job.created_at else ""
        accepted_on = job.updated_at.isoformat() if job.updated_at else ""

        entry = {
            "job_id": job.id,
            "client": client_name,
            "client_phone": client_phone,
            "client_email": client_email,
            "total_amount": total_amount,
            "property_address": job.property_address,
            "preferred_date": job.preferred_date if job.preferred_date else "",
            "deposit_amount": deposit_amount,
            "remaining_amount": remaining_amount,
            "quote_notes": job.quote_notes if job.quote_notes else "",
            "quoted_on": quoted_on,
            "accepted_on": accepted_on,
            "status": "BOOKING CONFIRMED",
            "property_photos": job.property_photos if job.property_photos else "",
            "additional_information": job.additional_information if job.additional_information else ""
        }
        if waste_names is not None:
            entry["waste_types"] = waste_names
        result.append(entry)
    
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

# Removed: GET /admin/crew/available - endpoint removed per request
# Removed: GET /admin/crew/available and POST /admin/jobs/{job_id}/assign-crew/{crew_id}
# These endpoints were removed per request. Crew assignment and availability
# logic should be handled by the admin UI or a separate service. If you want
# a replacement or a more restricted/batched assignment endpoint, tell me and
# I will add it.

# Removed: GET /admin/jobs/unassigned/{job_id} - endpoint removed per request
# Unassigned job details by ID are no longer exposed via the admin API.
# If you need a replacement (for example, a paged or limited view),
# I can add a tailored endpoint on request.

# Removed: GET /admin/jobs/{job_id}/available-crew - endpoint removed per request

# ============ JOB VERIFICATION ENDPOINTS ============

# Removed: GET /admin/verification/jobs - endpoint removed per request

# Removed: GET /admin/verification/jobs/{job_id} - Get Job Verification Details
# This endpoint was removed per request. Use the verification list and approve/reject
# endpoints to manage verification flow. If you need a replacement endpoint,
# I can add a tailored, simplified version.

# Removed: Job verification approve/reject/send-payment-request endpoints
# The following endpoints were intentionally removed per request:
# - POST /admin/verification/jobs/{job_id}/approve
# - POST /admin/verification/jobs/{job_id}/reject
# - POST /admin/verification/jobs/{job_id}/send-payment-request
#
# Verification and final payment workflows should be handled by an external
# service or a simplified admin UI action. If you want these restored with a
# specific, limited behavior, tell me and I will implement them.


# Removed: GET /admin/payments/completed - endpoint removed per request
# Completed payments listing is no longer exposed via the admin API.
# If a narrow or paged payment report is required, I can add a tailored
# endpoint on request.

# Removed: GET /admin/payments/pending - endpoint removed per request
# Pending payments overview is no longer exposed via the admin API.
# Request a narrower reporting endpoint if required.

# Removed: GET /admin/payments/pending/{job_id} - endpoint removed per request
# Detailed pending-payment-by-id endpoint removed. Payment details should
# be surfaced by a reporting service or via the client backend.
    
    deposit_amount = float(job.deposit_amount) if job.deposit_amount else 0.0
    remaining_amount = float(job.remaining_amount) if job.remaining_amount else 0.0
    total_amount = float(job.quote_amount) if job.quote_amount else 0.0
    
    if remaining_amount == 0.0 and total_amount > 0.0 and deposit_amount > 0.0:
        remaining_amount = total_amount - deposit_amount
    
    if job.status == "quote_accepted":
        payment_type = "Deposit Payment Pending"
        amount_due = deposit_amount
        status = "Pending"
    elif job.status in ["deposit_paid", "crew_assigned", "crew_arrived", "before_photo", "clearance_in_progress", "after_photo", "work_completed", "job_verified"]:
        payment_type = "Deposit Paid"
        amount_due = 0.0
        status = "Deposit Paid"
    elif job.status == "payment_pending":
        payment_type = "Remaining Amount Pending"
        amount_due = remaining_amount
        status = "Pending"
    else:
        payment_type = "Unknown"
        amount_due = 0.0
        status = "Unknown"
    
    return {
        "job_id": job.id,
        "client_name": client_name,
        "client_email": client_email,
        "client_phone": client_phone,
        "property_address": job.property_address,
        "service_type": service_type_name,
        "total_amount": total_amount,
        "deposit_amount": deposit_amount,
        "remaining_amount": remaining_amount,
        "amount_due": amount_due,
        "payment_type": payment_type,
        "status": status,
        "job_status": job.status,
        "preferred_date": job.preferred_date if job.preferred_date else "",
        "preferred_time": job.preferred_time if job.preferred_time else ""
    }

@router.post("/admin/quotes/{job_id}/reject", tags=["Admin"], summary="Reject Quote Request")
async def reject_quote_request(
    job_id: str,
    rejection_reason: str = Form(...),
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Admin rejects a quote request (job_created status)"""
    admin = db.query(Admin).filter(Admin.email == current_user.get("sub")).first()
    if not admin:
        raise HTTPException(status_code=403, detail="Admin access required")
    
    job = db.query(Job).filter(Job.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    
    if job.status != "job_created":
        raise HTTPException(status_code=400, detail="Can only reject jobs awaiting quote")
    
    job.status = "quote_rejected"
    job.decline_reason = rejection_reason
    db.commit()
    
    return {
        "message": "Quote request rejected successfully",
        "job_id": job.id,
        "status": job.status,
        "rejection_reason": rejection_reason
    }

@router.post("/admin/jobs/{job_id}/cancel", tags=["Admin"], summary="Cancel Job")
async def cancel_job_by_admin(
    job_id: str,
    cancellation_reason: str = Form(...),
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Admin cancels an ongoing job"""
    admin = db.query(Admin).filter(Admin.email == current_user.get("sub")).first()
    if not admin:
        raise HTTPException(status_code=403, detail="Admin access required")
    
    job = db.query(Job).filter(Job.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    
    # Cannot cancel completed or already cancelled jobs
    if job.status in ["job_completed", "cancelled", "admin_rejected"]:
        raise HTTPException(status_code=400, detail=f"Cannot cancel job with status: {job.status}")
    
    # If crew was assigned, set them back to available
    if job.assigned_crew_id:
        crew = db.query(Crew).filter(Crew.id == job.assigned_crew_id).first()
        if crew:
            crew.status = "available"
    
    job.status = "cancelled"
    job.cancellation_reason = cancellation_reason
    db.commit()
    
    return {
        "message": "Job cancelled successfully",
        "job_id": job.id,
        "status": job.status,
        "cancellation_reason": cancellation_reason
    }

# Removed: GET /admin/jobs/rejected-cancelled - endpoint removed per request
# Rejected/cancelled jobs listing is no longer exposed via the admin API.
# If a filtered or audited view is required, I can add a tailored report endpoint.

# Removed: GET /admin/jobs/verified - endpoint removed per request
# Verified jobs listing is no longer exposed via the admin API. Request a
# tailored report if a verification summary is needed.

 # Removed: GET /admin/jobs/verified/{job_id} - endpoint removed per request
 # Detailed verified-job-by-id endpoint removed. If specific verification
 # details must be available, we can implement a limited view on request.
