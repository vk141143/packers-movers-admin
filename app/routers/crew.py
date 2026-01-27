from fastapi import APIRouter, Depends, HTTPException, Query, Form
from sqlalchemy.orm import Session
from app.database.db import get_db
from app.models.crew import Crew, Admin
from app.schemas.crew import CrewResponse
from app.core.security import get_current_user
from typing import List, Optional

router = APIRouter()

@router.patch("/crew/profile", tags=["Crew"])
async def update_crew_profile(
    full_name: Optional[str] = Form(None),
    phone_number: Optional[str] = Form(None),
    bank_name: Optional[str] = Form(None),
    account_number: Optional[str] = Form(None),
    sort_code: Optional[str] = Form(None),
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    crew = db.query(Crew).filter(Crew.email == current_user.get("sub")).first()
    if not crew:
        raise HTTPException(status_code=404, detail="Crew not found")
    
    if full_name:
        crew.full_name = full_name
    if phone_number:
        crew.phone_number = phone_number
    if bank_name:
        crew.bank_name = bank_name
    if account_number:
        crew.account_number = account_number
    if sort_code:
        crew.sort_code = sort_code
    
    db.commit()
    db.refresh(crew)
    
    return {
        "message": "Profile updated successfully",
        "crew": {
            "id": crew.id,
            "email": crew.email,
            "full_name": crew.full_name,
            "phone_number": crew.phone_number,
            "bank_name": crew.bank_name,
            "account_number": crew.account_number,
            "sort_code": crew.sort_code
        }
    }

@router.get("/crew/profile", tags=["Crew"])
async def get_crew_profile(
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    crew = db.query(Crew).filter(Crew.email == current_user.get("sub")).first()
    if not crew:
        raise HTTPException(status_code=404, detail="Crew not found")
    
    return {
        "id": crew.id,
        "email": crew.email,
        "full_name": crew.full_name,
        "phone_number": crew.phone_number,
        "bank_name": crew.bank_name,
        "account_number": crew.account_number,
        "sort_code": crew.sort_code,
        "status": crew.status,
        "is_approved": crew.is_approved
    }

@router.get("/crew/admin-info", tags=["Crew"], summary="Get Admin Organization Info")
async def get_admin_info(
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    crew = db.query(Crew).filter(Crew.email == current_user.get("sub")).first()
    if not crew:
        raise HTTPException(status_code=403, detail="Crew access required")
    
    admin = db.query(Admin).first()
    if not admin:
        return {"organization_name": "", "department": ""}
    
    return {
        "organization_name": admin.organization_name if admin.organization_name else "",
        "department": admin.department if admin.department else ""
    }
