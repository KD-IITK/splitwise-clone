from datetime import datetime
from uuid import UUID
from pydantic import BaseModel, EmailStr, Field

class InvitationCreate(BaseModel):
    recipient_email: EmailStr

class InvitationResponse(BaseModel):
    invitation_id: UUID
    group_id: UUID
    recipient_email: EmailStr
    expiration_date: datetime
    status: str

class InvitationAccept(BaseModel):
    username: str = Field(min_length=1, max_length=50)