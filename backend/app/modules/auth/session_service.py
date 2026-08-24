import uuid
from datetime import datetime, timedelta, timezone
from app.db import get_connection

SESSION_DURATION_DAYS = 7

def create_session(user_id: uuid.UUID):
    connection = get_connection()
    cursor = connection.cursor()
    now = datetime.now(timezone.utc)
    expires_at = now + timedelta(days=SESSION_DURATION_DAYS)
    try:
        cursor.execute(
            """
            INSERT INTO sessions (
                user_id,
                expires_at
            )
            VALUES (%s, %s)
            RETURNING session_id, expires_at;
            """,
            (user_id, expires_at)
        )
        row = cursor.fetchone()
        connection.commit()
        return {
            "session_id": row[0],
            "expires_at": row[1]
        }
    finally:
        cursor.close()
        connection.close()

        
def revoke_session(session_id: uuid.UUID):
    connection = get_connection()
    cursor = connection.cursor()
    now = datetime.now(timezone.utc)
    try:
        cursor.execute(
            """
            UPDATE sessions
            SET revoked_at = %s
            WHERE session_id = %s
              AND revoked_at IS NULL;
            """,
            (now, session_id)
        )
        connection.commit()
    finally:
        cursor.close()
        connection.close()

def get_user_id_from_session(session_id: uuid):
    connection = get_connection()
    cursor = connection.cursor()

    try:
        cursor.execute(
            """
            SELECT user_id
            FROM sessions
            WHERE session_id = %s;
            """,
            (session_id,)
        )
        row = cursor.fetchone()
        if row is None:
            return None
        return row[0]
    finally:
        cursor.close()
        connection.close()