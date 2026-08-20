from datetime import datetime
from uuid import UUID

from pydantic import BaseModel


class UserCreate(BaseModel):
    email_id: str

class UserResponse(BaseModel):
    user_id: UUID
    email_id: str
    created_at: datetime