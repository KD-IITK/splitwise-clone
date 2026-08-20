from fastapi import APIRouter

from app.modules.users.schemas import UserCreate, UserResponse
from app.modules.users.service import create_user, get_users


router = APIRouter(
    prefix="/api/users",
    tags=["Users"]
)


@router.get("/", response_model=list[UserResponse])
def get_all_users():
    return get_users()

@router.post("/", response_model=UserResponse, status_code=201)
def create_new_user(user: UserCreate):
    return create_user(user)
