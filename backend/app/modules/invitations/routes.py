from uuid import UUID
from fastapi import APIRouter, Depends, status, HTTPException
from app.core.dependencies import get_current_user
from app.modules.invitations.schemas import (InvitationCreate, InvitationResponse, InvitationAccept)
from app.modules.invitations.service import create_invitation,  get_invitation, accept_invitation
from app.modules.users.service import get_user_email
from datetime import datetime, timezone

router = APIRouter(
    prefix="/api/groups/{group_id}/invitations",
    tags=["Invitations"]
)


@router.post("/", response_model=InvitationResponse, status_code=status.HTTP_201_CREATED)
def create_new_invitation(group_id: UUID, request: InvitationCreate, user_id=Depends(get_current_user)):
    return create_invitation(
        group_id=group_id,
        inviter_id=user_id,
        recipient_email=str(request.recipient_email)
    )

@router.get("/{invitation_id}")
def view_invitation(invitation_id: UUID, user_id=Depends(get_current_user)):
    invitation = get_invitation(invitation_id)

    if invitation["recipient_email"] != get_user_email(user_id):
        raise HTTPException(
            status_code=403,
            detail="This invitation is not for your account."
        )

    if invitation["expiration_date"] <= datetime.now(timezone.utc):
        raise HTTPException(
            status_code=410,
            detail="Invitation has expired."
        )

    if invitation["status"] == "ACCEPTED":
        raise HTTPException(
            status_code=409,
            detail="Invitation has already been accepted."
        )

    return {
        "invitation_id": invitation["invitation_id"],
        "status": invitation["status"],
        "expiration_date": invitation["expiration_date"]
    }

@router.post("/{invitation_id}/accept")
def accept_invitation_route(invitation_id: UUID, request: InvitationAccept, user_id=Depends(get_current_user)):
    return accept_invitation(
        invitation_id=invitation_id,
        user_id=user_id,
        username=request.username
    )