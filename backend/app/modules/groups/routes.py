from fastapi import APIRouter, Depends
from uuid import UUID
from app.core.dependencies import get_current_user
from app.modules.groups.schemas import GroupCreate, GroupResponse, GroupListItem, GroupDetails
from app.modules.groups.service import create_group, get_user_groups, get_group_details


router = APIRouter(
    prefix="/api/groups",
    tags=["Groups"]
)


@router.post("/", response_model=GroupResponse, status_code=201)
def create_new_group(request: GroupCreate, user_id=Depends(get_current_user)):
    return create_group(
        group_name=request.group_name,
        user_id=user_id,
        username=request.username
    )

@router.get("/", response_model=list[GroupListItem])
def list_groups(user_id=Depends(get_current_user)):
    return get_user_groups(user_id)

@router.get( "/{group_id}", response_model=GroupDetails)
def get_group(group_id: UUID, user_id=Depends(get_current_user)):
    return get_group_details(
        group_id=group_id,
        user_id=user_id
    )