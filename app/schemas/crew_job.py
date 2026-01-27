from pydantic import BaseModel
from typing import Optional

class UpdateJobStatusRequest(BaseModel):
    status: str

class SendOTPRequest(BaseModel):
    otp: str

class UploadPhotoRequest(BaseModel):
    photo_type: str  # "before" or "after"
