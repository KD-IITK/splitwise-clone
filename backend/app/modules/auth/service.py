import hashlib
import secrets
import hmac
import os

from datetime import datetime, timedelta, timezone
from app.db import get_connection
from fastapi import HTTPException

from app.modules.users.service import (
    create_user_from_email,
    get_user_by_email,
)

from app.modules.auth.session_service import create_session

def generate_otp():
    return f"{secrets.randbelow(1_000_000):06d}"

OTP_HASH_SECRET = os.environ["OTP_HASH_SECRET"]
def hash_otp(otp: str) -> str:
    return hmac.new(
        OTP_HASH_SECRET.encode(),
        otp.encode(),
        hashlib.sha256
    ).hexdigest()


def create_otp(email_id: str):
    connection = get_connection()
    cursor = connection.cursor()

    now = datetime.now(timezone.utc)

    try:
        # Check the most recent OTP for this email
        cursor.execute(
            """
            SELECT
                expires_at,
                blocked_until,
                verified_at
            FROM otp_verifications
            WHERE email_id = %s
            ORDER BY created_at DESC
            LIMIT 1;
            """,
            (email_id,)
        )

        previous_otp = cursor.fetchone()

        if previous_otp:
            expires_at, blocked_until, verified_at = previous_otp

            # Check whether the user is currently blocked
            if blocked_until is not None and blocked_until > now:
                raise HTTPException(
                    status_code=429,
                    detail="OTP verification is temporarily blocked."
                )
            # Check whether there is still an active OTP
            if expires_at > now and verified_at is None:
                raise HTTPException(
                    status_code=429,
                    detail="An OTP is already active. Please wait for it to expire."
                )

        # Generate a new OTP
        otp = generate_otp()
        otp_hash = hash_otp(otp)

        expires_at = now + timedelta(minutes=1)
        cursor.execute(
            """
            INSERT INTO otp_verifications (
                email_id,
                otp_hash,
                expires_at
            )
            VALUES (%s, %s, %s);
            """,
            (email_id, otp_hash, expires_at)
        )

        connection.commit()
        return otp

    except HTTPException:
        connection.rollback()
        raise

    finally:
        cursor.close()
        connection.close()


def verify_otp(email_id: str, otp: str):
    connection = get_connection()
    cursor = connection.cursor()

    now = datetime.now(timezone.utc)
    try:
        cursor.execute(
            """
            SELECT
                otp_id,
                otp_hash,
                expires_at,
                failed_attempts,
                blocked_until,
                verified_at
            FROM otp_verifications
            WHERE email_id = %s
            ORDER BY created_at DESC
            LIMIT 1;
            """,
            (email_id,)
        )

        record = cursor.fetchone()

        if record is None:
            raise HTTPException(
                status_code=400,
                detail="No OTP has been requested."
            )

        (
            otp_id,
            otp_hash,
            expires_at,
            failed_attempts,
            blocked_until,
            verified_at
        ) = record

        # Check whether verification is blocked
        if blocked_until is not None and blocked_until > now:
            raise HTTPException(
                status_code=429,
                detail="OTP verification is temporarily blocked."
            )

        # Check whether OTP has already been used
        if verified_at is not None:
            raise HTTPException(
                status_code=400,
                detail="OTP has already been used."
            )

        # Check expiration
        if expires_at <= now:
            raise HTTPException(
                status_code=400,
                detail="OTP has expired."
            )

        # Check OTP
        if hash_otp(otp) != otp_hash:
            failed_attempts += 1
            if failed_attempts >= 5:
                blocked_until = now + timedelta(minutes=5)
                cursor.execute(
                    """
                    UPDATE otp_verifications
                    SET
                        failed_attempts = %s,
                        blocked_until = %s
                    WHERE otp_id = %s;
                    """,
                    (
                        failed_attempts,
                        blocked_until,
                        otp_id
                    )
                )

                connection.commit()

                raise HTTPException(
                    status_code=429,
                    detail="Too many incorrect attempts. Verification is blocked for 5 minutes."
                )

            cursor.execute(
                """
                UPDATE otp_verifications
                SET failed_attempts = %s
                WHERE otp_id = %s;
                """,
                (
                    failed_attempts,
                    otp_id
                )
            )

            connection.commit()

            raise HTTPException(
                status_code=400,
                detail="Incorrect OTP."
            )

        # Correct OTP
        cursor.execute(
            """
            UPDATE otp_verifications
            SET verified_at = %s
            WHERE otp_id = %s;
            """,
            (now, otp_id)
        )
        connection.commit()
        user = get_user_by_email(email_id)
        if user is None:
            user = create_user_from_email(email_id)
        session = create_session(user["user_id"])
        return {
            "message": "Login successful.",
            "session_id": str(session["session_id"]),
            "expires_at": session["expires_at"]
        }
    finally:
        cursor.close()
        connection.close()