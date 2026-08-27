from uuid import UUID
from fastapi import APIRouter, Depends
from app.core.dependencies import get_current_user
from app.modules.settlements.schemas import UserBalance, SettlementCreate, SettlementResponse, DebtResponse
from app.modules.settlements.service import get_group_balances, create_settlement, get_group_settlements, get_pairwise_debts, get_simplified_debts

router = APIRouter(
    prefix="/api/groups/{group_id}",
    tags=["Settlements"]
)


@router.get("/balances",response_model=list[UserBalance])
def get_balances(group_id: UUID, user_id=Depends(get_current_user)):
    return get_group_balances(
        group_id=group_id,
        user_id=user_id,
    )

@router.post("/settlements", response_model=SettlementResponse, status_code=201)
def create_new_settlement(
    group_id: UUID,
    request: SettlementCreate,
    user_id=Depends(get_current_user)
):
    return create_settlement(
        group_id=group_id,
        user_id=user_id,
        request=request,
    )

@router.get("/settlements", response_model=list[SettlementResponse])
def list_settlements(group_id: UUID, user_id=Depends(get_current_user)):
    return get_group_settlements(
        group_id=group_id,
        user_id=user_id,
    )

@router.get("/debts", response_model=list[DebtResponse])
def get_debts(group_id: UUID, user_id=Depends(get_current_user)):
    return get_pairwise_debts(
        group_id=group_id,
        user_id=user_id,
    )

@router.get("/debts/simplified",response_model=list[DebtResponse])
def get_simplified(group_id: UUID,user_id=Depends(get_current_user)):
    return get_simplified_debts(
        group_id=group_id,
        user_id=user_id,
    )