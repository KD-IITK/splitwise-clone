from pydantic import BaseModel, Field
from uuid import UUID
from datetime import datetime

class GroupCreate(BaseModel):
    group_name: str = Field(min_length=1, max_length=100)
    username: str = Field(min_length=1, max_length=50)

class GroupResponse(BaseModel):
    group_id: UUID
    group_name: str
    created_at: datetime

class GroupListItem(BaseModel):
    group_id: UUID
    group_name: str
    username: str

class GroupMember(BaseModel):
    user_id: UUID
    username: str
    
class GroupDetails(BaseModel):
    group_id: UUID
    group_name: str
    members: list[GroupMember]
