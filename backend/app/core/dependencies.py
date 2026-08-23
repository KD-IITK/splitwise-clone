from uuid import UUID

from fastapi import Cookie, HTTPException

from app.modules.auth.session_service import get_user_id_from_session


def get_current_user(session_id: str | None = Cookie(default=None)):
    if session_id is None:
        raise HTTPException(
            status_code=401,
            detail="Not authenticated."
        )

    try:
        session_uuid = UUID(session_id)
    except ValueError:
        raise HTTPException(
            status_code=401,
            detail="Invalid session."
        )

    user_id = get_user_id_from_session(session_uuid)

    if user_id is None:
        raise HTTPException(
            status_code=401,
            detail="Not authenticated."
        )

    return user_id