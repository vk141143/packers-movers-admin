from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form
from fastapi.openapi.models import Example
from sqlalchemy.orm import Session
from app.database.db import get_db
from app.models.crew import Crew, Admin
from app.schemas.auth import AdminRegister, LoginRequest, TokenResponse, UserResponse, RefreshTokenRequest, UpdateProfile, ForgotPasswordRequest, VerifyForgotOTPRequest, ResetPasswordRequest
from app.core.security import hash_password, verify_password, create_access_token, create_refresh_token, verify_refresh_token, get_current_user
from app.core.email import send_admin_notification, send_approval_email, send_otp_email
from app.core.storage import storage
from typing import Optional, List

router = APIRouter()

@router.post("/register/crew", response_model=UserResponse, status_code=status.HTTP_201_CREATED, tags=["Authentication"])
async def register_crew(
    email: str = Form(None),
    full_name: str = Form(None),
    password: str = Form(None),
    phone_number: str = Form(None),
    drivers_license: UploadFile = File(default=None),
    dbs_certificate: UploadFile = File(default=None),
    proof_of_address: UploadFile = File(default=None),
    insurance_certificate: UploadFile = File(default=None),
    right_to_work: UploadFile = File(default=None),
    db: Session = Depends(get_db)
):
    existing_user = db.query(Crew).filter(Crew.email == email).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    new_user = Crew(
        email=email,
        full_name=full_name,
        password_hash=hash_password(password),
        phone_number=phone_number,
        is_approved=False
    )
    
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    # Upload documents to Utho storage
    crew_id = new_user.id
    
    if drivers_license and drivers_license.filename:
        url = storage.upload_crew_document(drivers_license.file, crew_id, "drivers_license", drivers_license.filename)
        if url:
            new_user.drivers_license = url
            print(f"Uploaded drivers_license: {url}")
    
    if dbs_certificate and dbs_certificate.filename:
        url = storage.upload_crew_document(dbs_certificate.file, crew_id, "dbs_certificate", dbs_certificate.filename)
        if url:
            new_user.dbs_certificate = url
            print(f"Uploaded dbs_certificate: {url}")
    
    if proof_of_address and proof_of_address.filename:
        url = storage.upload_crew_document(proof_of_address.file, crew_id, "proof_of_address", proof_of_address.filename)
        if url:
            new_user.proof_of_address = url
            print(f"Uploaded proof_of_address: {url}")
    
    if insurance_certificate and insurance_certificate.filename:
        url = storage.upload_crew_document(insurance_certificate.file, crew_id, "insurance_certificate", insurance_certificate.filename)
        if url:
            new_user.insurance_certificate = url
            print(f"Uploaded insurance_certificate: {url}")
    
    if right_to_work and right_to_work.filename:
        url = storage.upload_crew_document(right_to_work.file, crew_id, "right_to_work", right_to_work.filename)
        if url:
            new_user.right_to_work = url
            print(f"Uploaded right_to_work: {url}")
    
    db.commit()
    db.refresh(new_user)
    
    send_admin_notification(email, full_name)
    
    return new_user

@router.post("/register/admin", response_model=UserResponse, status_code=status.HTTP_201_CREATED, tags=["Authentication"])
def register_admin(admin_data: AdminRegister, db: Session = Depends(get_db)):
    existing_user = db.query(Admin).filter(Admin.email == admin_data.email).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    new_user = Admin(
        email=admin_data.email,
        full_name=admin_data.full_name,
        password_hash=hash_password(admin_data.password),
        phone_number=admin_data.phone_number
    )
    
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    return new_user

@router.post("/login/crew", response_model=TokenResponse, tags=["Authentication"])
def login_crew(login_data: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(Crew).filter(Crew.email == login_data.email).first()
    
    if not user or not verify_password(login_data.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )
    
    if not user.is_approved:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Your account is pending admin approval"
        )
    
    access_token = create_access_token({"sub": user.email, "role": "Crew"})
    refresh_token = create_refresh_token({"sub": user.email, "role": "Crew"})
    
    return TokenResponse(access_token=access_token, refresh_token=refresh_token)

@router.post("/login/admin", response_model=TokenResponse, tags=["Authentication"])
def login_admin(login_data: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(Admin).filter(Admin.email == login_data.email).first()
    
    if not user or not verify_password(login_data.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )
    
    access_token = create_access_token({"sub": user.email, "role": "Admin"})
    refresh_token = create_refresh_token({"sub": user.email, "role": "Admin"})
    
    return TokenResponse(access_token=access_token, refresh_token=refresh_token)

@router.post("/refresh", response_model=TokenResponse, tags=["Authentication"])
def refresh_token(request: RefreshTokenRequest, db: Session = Depends(get_db)):
    payload = verify_refresh_token(request.refresh_token)
    
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token"
        )
    
    role = payload.get("role")
    if role == "Crew":
        user = db.query(Crew).filter(Crew.email == payload.get("sub")).first()
    else:
        user = db.query(Admin).filter(Admin.email == payload.get("sub")).first()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found"
        )
    
    access_token = create_access_token({"sub": user.email, "role": role})
    refresh_token = create_refresh_token({"sub": user.email, "role": role})
    
    return TokenResponse(access_token=access_token, refresh_token=refresh_token)

@router.get("/crew/profile", tags=["Crew"])
def get_crew_profile(current_user: dict = Depends(get_current_user), db: Session = Depends(get_db)):
    from sqlalchemy import func
    from app.models.job import Job
    
    crew = db.query(Crew).filter(Crew.email == current_user["sub"]).first()
    if not crew:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Crew not found")
    
    # Fetch admin details (assuming there's one admin or get the first one)
    admin = db.query(Admin).first()
    
    # Calculate average rating
    avg_rating = db.query(func.avg(Job.rating)).filter(
        Job.assigned_crew_id == crew.id,
        Job.rating.isnot(None)
    ).scalar()
    
    return {
        "id": crew.id,
        "email": crew.email,
        "full_name": crew.full_name,
        "phone_number": crew.phone_number,
        "address": getattr(crew, 'address', None),
        "is_approved": crew.is_approved,
        "status": crew.status,
        "rating": round(float(avg_rating), 2) if avg_rating else 0.0,
        "organization_name": admin.organization_name if admin and admin.organization_name else None,
        "department": admin.department if admin and admin.department else None,
        "created_at": crew.created_at
    }

@router.patch("/crew/profile", tags=["Crew"])
async def update_crew_profile(
    full_name: str = Form(None),
    phone_number: str = Form(None),
    address: str = Form(None),
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    crew = db.query(Crew).filter(Crew.email == current_user["sub"]).first()
    if not crew:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Crew not found")
    
    if full_name:
        crew.full_name = full_name
    if phone_number:
        crew.phone_number = phone_number
    if address:
        crew.address = address
    
    db.commit()
    db.refresh(crew)
    return {
        "id": crew.id,
        "email": crew.email,
        "full_name": crew.full_name,
        "phone_number": crew.phone_number,
        "address": crew.address,
        "is_approved": crew.is_approved,
        "created_at": crew.created_at
    }

# Forgot Password for Crew
@router.post("/forgot-password/crew", tags=["Authentication"])
def forgot_password_crew(data: ForgotPasswordRequest, db: Session = Depends(get_db)):
    import random
    from datetime import datetime, timedelta
    from app.core.sms import send_sms_otp
    
    # Find user by email or phone
    if data.contact_method == "email":
        user = db.query(Crew).filter(Crew.email == data.email).first()
    else:  # phone
        user = db.query(Crew).filter(Crew.phone_number == data.phone_number).first()
    
    if user and user.is_approved:
        otp = str(random.randint(1000, 9999))
        user.reset_otp = otp
        user.reset_otp_expiry = datetime.utcnow() + timedelta(minutes=5)
        db.commit()
        
        # Send OTP via chosen method
        if data.contact_method == "email":
            send_otp_email(data.email, otp)
        else:  # phone
            send_sms_otp(data.phone_number, otp)
    
    return {
        "message": f"If {'email' if data.contact_method == 'email' else 'phone number'} exists, OTP has been sent",
        "contact_method": data.contact_method
    }

@router.post("/verify-forgot-otp/crew", tags=["Authentication"])
def verify_forgot_otp_crew(data: VerifyForgotOTPRequest, db: Session = Depends(get_db)):
    import secrets
    from datetime import datetime, timedelta
    
    # Find user by email or phone
    if data.contact_method == "email":
        user = db.query(Crew).filter(Crew.email == data.email).first()
    else:  # phone
        user = db.query(Crew).filter(Crew.phone_number == data.phone_number).first()
    
    if not user:
        raise HTTPException(status_code=400, detail="Invalid OTP")
    
    if not user.reset_otp or user.reset_otp != data.otp:
        raise HTTPException(status_code=400, detail="Invalid OTP")
    
    if user.reset_otp_expiry < datetime.utcnow():
        raise HTTPException(status_code=400, detail="OTP expired")
    
    reset_token = secrets.token_urlsafe(32)
    user.reset_token = reset_token
    user.reset_token_expiry = datetime.utcnow() + timedelta(minutes=15)
    user.reset_otp = None
    user.reset_otp_expiry = None
    
    db.commit()
    
    return {
        "message": "OTP verified successfully",
        "reset_token": reset_token
    }

@router.post("/reset-password/crew", tags=["Authentication"])
def reset_password_crew(data: ResetPasswordRequest, db: Session = Depends(get_db)):
    from datetime import datetime
    
    if data.new_password != data.confirm_password:
        raise HTTPException(status_code=400, detail="Passwords do not match")
    
    if len(data.new_password) < 8:
        raise HTTPException(status_code=400, detail="Password must be at least 8 characters")
    
    user = db.query(Crew).filter(Crew.reset_token == data.reset_token).first()
    
    if not user:
        raise HTTPException(status_code=400, detail="Invalid reset token")
    
    if user.reset_token_expiry < datetime.utcnow():
        raise HTTPException(status_code=400, detail="Reset token expired")
    
    user.password_hash = hash_password(data.new_password)
    user.reset_token = None
    user.reset_token_expiry = None
    
    db.commit()
    
    return {"message": "Password reset successfully"}

# Forgot Password for Admin
@router.post("/forgot-password/admin", tags=["Authentication"])
def forgot_password_admin(data: ForgotPasswordRequest, db: Session = Depends(get_db)):
    import random
    from datetime import datetime, timedelta
    from app.core.sms import send_sms_otp
    
    # Find user by email or phone
    if data.contact_method == "email":
        user = db.query(Admin).filter(Admin.email == data.email).first()
    else:  # phone
        user = db.query(Admin).filter(Admin.phone_number == data.phone_number).first()
    
    if user:
        otp = str(random.randint(1000, 9999))
        user.reset_otp = otp
        user.reset_otp_expiry = datetime.utcnow() + timedelta(minutes=5)
        db.commit()
        
        # Send OTP via chosen method
        if data.contact_method == "email":
            send_otp_email(data.email, otp)
        else:  # phone
            send_sms_otp(data.phone_number, otp)
    
    return {
        "message": f"If {'email' if data.contact_method == 'email' else 'phone number'} exists, OTP has been sent",
        "contact_method": data.contact_method
    }

@router.post("/verify-forgot-otp/admin", tags=["Authentication"])
def verify_forgot_otp_admin(data: VerifyForgotOTPRequest, db: Session = Depends(get_db)):
    import secrets
    from datetime import datetime, timedelta
    
    # Find user by email or phone
    if data.contact_method == "email":
        user = db.query(Admin).filter(Admin.email == data.email).first()
    else:  # phone
        user = db.query(Admin).filter(Admin.phone_number == data.phone_number).first()
    
    if not user:
        raise HTTPException(status_code=400, detail="Invalid OTP")
    
    if not user.reset_otp or user.reset_otp != data.otp:
        raise HTTPException(status_code=400, detail="Invalid OTP")
    
    if user.reset_otp_expiry < datetime.utcnow():
        raise HTTPException(status_code=400, detail="OTP expired")
    
    reset_token = secrets.token_urlsafe(32)
    user.reset_token = reset_token
    user.reset_token_expiry = datetime.utcnow() + timedelta(minutes=15)
    user.reset_otp = None
    user.reset_otp_expiry = None
    
    db.commit()
    
    return {
        "message": "OTP verified successfully",
        "reset_token": reset_token
    }

@router.post("/reset-password/admin", tags=["Authentication"])
def reset_password_admin(data: ResetPasswordRequest, db: Session = Depends(get_db)):
    from datetime import datetime
    
    if data.new_password != data.confirm_password:
        raise HTTPException(status_code=400, detail="Passwords do not match")
    
    if len(data.new_password) < 8:
        raise HTTPException(status_code=400, detail="Password must be at least 8 characters")
    
    user = db.query(Admin).filter(Admin.reset_token == data.reset_token).first()
    
    if not user:
        raise HTTPException(status_code=400, detail="Invalid reset token")
    
    if user.reset_token_expiry < datetime.utcnow():
        raise HTTPException(status_code=400, detail="Reset token expired")
    
    user.password_hash = hash_password(data.new_password)
    user.reset_token = None
    user.reset_token_expiry = None
    
    db.commit()
    
    return {"message": "Password reset successfully"}

@router.get("/admin/profile", tags=["Admin"])
def get_admin_profile(current_user: dict = Depends(get_current_user), db: Session = Depends(get_db)):
    admin = db.query(Admin).filter(Admin.email == current_user["sub"]).first()
    if not admin:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Admin not found")
    
    return {
        "id": admin.id,
        "email": admin.email,
        "full_name": admin.full_name,
        "organization_name": admin.organization_name,
        "phone_number": admin.phone_number,
        "contact_person": admin.contact_person,
        "department": admin.department,
        "business_address": admin.business_address,
        "account_type": "Admin",
        "status": "Active",
        "verification": "Verified",
        "created_at": admin.created_at
    }

@router.patch("/admin/profile", tags=["Admin"])
async def update_admin_profile(
    organization_name: str = Form(None),
    phone_number: str = Form(None),
    contact_person: str = Form(None),
    department: str = Form(None),
    business_address: str = Form(None),
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    admin = db.query(Admin).filter(Admin.email == current_user["sub"]).first()
    if not admin:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Admin not found")
    
    if organization_name:
        admin.organization_name = organization_name
    if phone_number:
        admin.phone_number = phone_number
    if contact_person:
        admin.contact_person = contact_person
    if department:
        admin.department = department
    if business_address:
        admin.business_address = business_address
    
    db.commit()
    db.refresh(admin)
    
    return {
        "id": admin.id,
        "email": admin.email,
        "full_name": admin.full_name,
        "organization_name": admin.organization_name,
        "phone_number": admin.phone_number,
        "contact_person": admin.contact_person,
        "department": admin.department,
        "business_address": admin.business_address,
        "created_at": admin.created_at
    }

@router.post("/resend-otp/crew", tags=["Authentication"])
def resend_otp_crew(data: ForgotPasswordRequest, db: Session = Depends(get_db)):
    import random
    from datetime import datetime, timedelta
    from app.core.sms import send_sms_otp
    
    if data.contact_method == "email":
        user = db.query(Crew).filter(Crew.email == data.email).first()
    else:
        user = db.query(Crew).filter(Crew.phone_number == data.phone_number).first()
    
    if user and user.is_approved:
        otp = str(random.randint(1000, 9999))
        user.reset_otp = otp
        user.reset_otp_expiry = datetime.utcnow() + timedelta(minutes=5)
        db.commit()
        
        if data.contact_method == "email":
            send_otp_email(data.email, otp)
        else:
            send_sms_otp(data.phone_number, otp)
    
    return {
        "message": f"OTP resent successfully via {data.contact_method}",
        "contact_method": data.contact_method
    }

@router.post("/resend-otp/admin", tags=["Authentication"])
def resend_otp_admin(data: ForgotPasswordRequest, db: Session = Depends(get_db)):
    import random
    from datetime import datetime, timedelta
    from app.core.sms import send_sms_otp
    
    if data.contact_method == "email":
        user = db.query(Admin).filter(Admin.email == data.email).first()
    else:
        user = db.query(Admin).filter(Admin.phone_number == data.phone_number).first()
    
    if user:
        otp = str(random.randint(1000, 9999))
        user.reset_otp = otp
        user.reset_otp_expiry = datetime.utcnow() + timedelta(minutes=5)
        db.commit()
        
        if data.contact_method == "email":
            send_otp_email(data.email, otp)
        else:
            send_sms_otp(data.phone_number, otp)
    
    return {
        "message": f"OTP resent successfully via {data.contact_method}",
        "contact_method": data.contact_method
    }
