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
import re

router = APIRouter()

@router.post("/register/admin", response_model=UserResponse, status_code=status.HTTP_201_CREATED, tags=["Authentication"])
def register_admin(admin_data: AdminRegister, db: Session = Depends(get_db)):
    existing_user = db.query(Admin).filter(Admin.email == admin_data.email).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Check for duplicate phone number
    if admin_data.phone_number:
        existing_phone = db.query(Admin).filter(Admin.phone_number == admin_data.phone_number).first()
        if existing_phone:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Phone number already registered"
            )
    
    try:
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
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Registration failed: {str(e)}")

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
        if data.contact_method == "email":
            # Email OTP - store in DB
            otp = str(random.randint(100000, 999999))  # 6-digit OTP
            user.reset_otp = otp
            user.reset_otp_expiry = datetime.utcnow() + timedelta(minutes=5)
            db.commit()
            send_otp_email(data.email, otp)
        else:  # phone - use Twilio (no DB storage)
            user.reset_otp = None
            user.reset_otp_expiry = None
            db.commit()
            send_sms_otp(data.phone_number)
    
    return {
        "message": f"If {'email' if data.contact_method == 'email' else 'phone number'} exists, OTP has been sent",
        "contact_method": data.contact_method
    }

@router.post("/verify-forgot-otp/admin", tags=["Authentication"])
def verify_forgot_otp_admin(data: VerifyForgotOTPRequest, db: Session = Depends(get_db)):
    import secrets
    from datetime import datetime, timedelta
    from app.core.sms import verify_sms_otp
    
    # Find user by email or phone
    if data.contact_method == "email":
        user = db.query(Admin).filter(Admin.email == data.email).first()
    else:  # phone
        user = db.query(Admin).filter(Admin.phone_number == data.phone_number).first()
    
    if not user:
        raise HTTPException(status_code=400, detail="Invalid OTP")
    
    # Verify based on contact method
    if data.contact_method == "phone":
        # Verify with Twilio
        if not verify_sms_otp(data.phone_number, data.otp):
            raise HTTPException(status_code=400, detail="Invalid OTP")
    else:
        # Verify from database for email
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
        "profile_photo": getattr(admin, 'profile_photo', None),
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
    profile_photo: UploadFile = File(None),
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
    
    if profile_photo and profile_photo.filename:
        photo_url = storage.upload_file(profile_photo.file, f"admin_profiles/{admin.id}", f"profile_{profile_photo.filename}")
        if photo_url:
            admin.profile_photo = photo_url
    
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
        "profile_photo": admin.profile_photo,
        "created_at": admin.created_at
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
        if data.contact_method == "email":
            # Email OTP - store in DB
            otp = str(random.randint(100000, 999999))  # 6-digit OTP
            user.reset_otp = otp
            user.reset_otp_expiry = datetime.utcnow() + timedelta(minutes=5)
            db.commit()
            send_otp_email(data.email, otp)
        else:  # phone - use Twilio (no DB storage)
            user.reset_otp = None
            user.reset_otp_expiry = None
            db.commit()
            send_sms_otp(data.phone_number)
    
    return {
        "message": f"OTP resent successfully via {data.contact_method}",
        "contact_method": data.contact_method
    }
