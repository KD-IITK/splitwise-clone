from fastapi import APIRouter, Response, Cookie, HTTPException, Depends
from uuid import UUID
from app.modules.auth.schemas import RequestOTP, VerifyOTP
from app.modules.auth.service import create_otp, verify_otp
from app.modules.auth.session_service import get_user_id_from_session, revoke_session
from app.core.dependencies import get_current_user

router = APIRouter(
    prefix="/api/auth",
    tags=["Authentication"]
)

@router.post("/request-otp")
def request_otp(request: RequestOTP):
    otp = create_otp(request.email_id)
    print(f"Development OTP for {request.email_id}: {otp}")
    return {
        "message": "OTP generated successfully.",
    }

@router.post("/verify-otp")
def verify_otp_route(request: VerifyOTP, response: Response):
    result = verify_otp(
        request.email_id,
        request.otp
    )

    response.set_cookie(
        key="session_id",
        value=str(result["session_id"]),
        httponly=True,
        secure=False, # change to true later
        samesite="lax",
        max_age=7 * 24 * 60 * 60
    )

    return {
        "message": "Login successful."
    }

@router.get("/me")
def get_me(user_id = Depends(get_current_user)):
    return {
        "user_id": str(user_id)
    }

@router.post("/logout")
def logout(response: Response,session_id: str | None = Cookie(default=None)):
    if session_id is not None:
        try:
            session_uuid = UUID(session_id)
            revoke_session(session_uuid)
        except ValueError:
            pass

    response.delete_cookie(
        key="session_id"
    )

    return {
        "message": "Logged out successfully."
    }