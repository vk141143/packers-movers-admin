from pydantic import BaseModel
from typing import List, Optional

class UpdateJobStatusRequest(BaseModel):
    status: str

class UploadPhotosRequest(BaseModel):
    photo_urls: List[str]
    type: str  # "before" or "after"

class VerifyOTPRequest(BaseModel):
    otp: str
