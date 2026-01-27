from pydantic import BaseModel

class CrewApprovalRequest(BaseModel):
    action: str  # "approve" or "reject"
