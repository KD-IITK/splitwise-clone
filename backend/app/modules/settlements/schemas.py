from uuid import UUID
from pydantic import BaseModel, Field
from datetime import datetime

class SettlementCreate(BaseModel):
    payer_id: UUID
    receiver_id: UUID
    amount: int = Field(gt=0)

class SettlementResponse(BaseModel):
    settlement_id: UUID
    group_id: UUID
    payer_id: UUID
    receiver_id: UUID
    amount: int
    created_at: datetime

class UserBalance(BaseModel):
    user_id: UUID
    balance: int

class DebtResponse(BaseModel):
    payer_id: UUID
    receiver_id: UUID
    amount: int