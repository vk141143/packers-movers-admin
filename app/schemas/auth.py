from pydantic import BaseModel, EmailStr, Field, validator
import re
from typing import Optional

class CrewRegister(BaseModel):
    email: EmailStr
    full_name: str = Field(..., min_length=2, max_length=100)
    password: str = Field(..., min_length=8)
    phone_number: Optional[str] = None
    drivers_license: Optional[str] = None
    dbs_certificate: Optional[str] = None
    proof_of_address: Optional[str] = None
    insurance_certificate: Optional[str] = None
    right_to_work: Optional[str] = None

    @validator('password')
    def validate_password(cls, v):
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters')
        return v

    @validator('full_name')
    def validate_full_name(cls, v):
        if not v.strip():
            raise ValueError('Full name cannot be empty')
        return v.strip()

class AdminRegister(BaseModel):
    email: EmailStr
    full_name: str = Field(..., min_length=2, max_length=100)
    password: str = Field(..., min_length=8)
    phone_number: Optional[str] = None

    @validator('password')
    def validate_password(cls, v):
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters')
        return v

    @validator('full_name')
    def validate_full_name(cls, v):
        if not v.strip():
            raise ValueError('Full name cannot be empty')
        return v.strip()

class LoginRequest(BaseModel):
    email: EmailStr
    password: str

class RefreshTokenRequest(BaseModel):
    refresh_token: str

class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"

class UserResponse(BaseModel):
    id: str
    email: str
    full_name: str
    phone_number: Optional[str] = None
    drivers_license: Optional[str] = None
    dbs_certificate: Optional[str] = None
    proof_of_address: Optional[str] = None
    insurance_certificate: Optional[str] = None
    right_to_work: Optional[str] = None
    is_approved: bool = False
    status: str = "available"

    class Config:
        from_attributes = True

class UpdateProfile(BaseModel):
    email: Optional[EmailStr] = None
    phone_number: Optional[str] = None

class ForgotPasswordRequest(BaseModel):
    contact_method: str = Field(..., description="Either 'email' or 'phone'")
    email: Optional[EmailStr] = None
    phone_number: Optional[str] = None
    
    @validator('contact_method')
    def validate_contact_method(cls, v):
        if v not in ['email', 'phone']:
            raise ValueError('contact_method must be either "email" or "phone"')
        return v
    
    @validator('phone_number', always=True)
    def validate_phone_or_email(cls, v, values):
        contact_method = values.get('contact_method')
        email = values.get('email')
        
        if contact_method == 'email' and not email:
            raise ValueError('email is required when contact_method is "email"')
        if contact_method == 'phone' and not v:
            raise ValueError('phone_number is required when contact_method is "phone"')
        return v

class VerifyForgotOTPRequest(BaseModel):
    contact_method: str = Field(..., description="Either 'email' or 'phone'")
    email: Optional[EmailStr] = None
    phone_number: Optional[str] = None
    otp: str = Field(..., min_length=6, max_length=6)
    
    @validator('contact_method')
    def validate_contact_method(cls, v):
        if v not in ['email', 'phone']:
            raise ValueError('contact_method must be either "email" or "phone"')
        return v

class ResetPasswordRequest(BaseModel):
    reset_token: str
    new_password: str = Field(..., min_length=8)
    confirm_password: str = Field(..., min_length=8)
