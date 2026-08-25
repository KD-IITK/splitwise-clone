from uuid import UUID
from fastapi import APIRouter, Depends, status

from app.core.dependencies import get_current_user
from app.modules.expenses.schemas import ExpenseCreate, ExpenseResponse, ExpenseDetails, ExpenseUpdate
from app.modules.expenses.service import create_expense, get_group_expenses, get_expense, update_expense, delete_expense

router = APIRouter(
    prefix="/api/groups/{group_id}/expenses",
    tags=["Expenses"]
)

@router.post("/", response_model=ExpenseResponse, status_code=status.HTTP_201_CREATED)
def create_new_expense(group_id: UUID, request: ExpenseCreate, user_id=Depends(get_current_user)):
    return create_expense(
        group_id=group_id,
        creator_id=user_id,
        request=request
    )

@router.get("/", response_model=list[ExpenseDetails])
def list_group_expenses(group_id: UUID, user_id=Depends(get_current_user)):
    return get_group_expenses(group_id, user_id)

@router.get("/{expense_id}", response_model=ExpenseDetails)
def get_single_expense(group_id: UUID, expense_id: UUID, user_id=Depends(get_current_user)):
    return get_expense(
        group_id=group_id, 
        expense_id=expense_id,
        user_id=user_id
    )

@router.put("/{expense_id}", response_model=ExpenseResponse)
def update_existing_expense(
    group_id: UUID,
    expense_id: UUID,
    request: ExpenseUpdate,
    user_id=Depends(get_current_user)
):
    return update_expense(
        group_id=group_id,
        expense_id=expense_id,
        user_id=user_id,
        request=request
    )

@router.delete("/{expense_id}")
def delete_existing_expense(group_id: UUID, expense_id: UUID, user_id=Depends(get_current_user)):
    return delete_expense(
        group_id=group_id,
        expense_id=expense_id,
        user_id=user_id
    )