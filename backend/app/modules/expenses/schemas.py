from pydantic import BaseModel, Field
from uuid import UUID
from typing import Literal
from datetime import datetime

class ExpenseParticipantInput(BaseModel):
    user_id: UUID
    share: int | None = None

class ExpenseCreate(BaseModel):
    description: str = Field(min_length=2, max_length=200)
    total_amount: int = Field(gt=0)
    paid_by: UUID
    split_method: Literal["EQUAL", "UNEQUAL"]
    participants: list[ExpenseParticipantInput]

class ExpenseResponse(BaseModel):
    expense_id: UUID
    group_id: UUID
    created_by: UUID
    paid_by: UUID
    description: str
    total_amount: int
    split_method: str
    created_at: datetime

class ExpenseParticipantResponse(BaseModel):
    user_id: UUID
    share: int

class ExpenseDetails(BaseModel):
    expense_id: UUID
    group_id: UUID
    created_by: UUID
    paid_by: UUID
    description: str
    total_amount: int
    split_method: str
    created_at: datetime
    participants: list[ExpenseParticipantResponse]

class ExpenseUpdate(BaseModel):
    description: str = Field(min_length=2, max_length=200)
    total_amount: int = Field(gt=0)
    paid_by: UUID
    split_method: Literal["EQUAL", "UNEQUAL"]
    participants: list[ExpenseParticipantInput]
