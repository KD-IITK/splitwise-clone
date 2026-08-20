from fastapi import HTTPException
from psycopg.errors import UniqueViolation

from app.db import get_connection
from app.modules.users.schemas import UserCreate


def create_user(user: UserCreate):

    connection = get_connection()
    cursor = connection.cursor()

    try:
        cursor.execute(
            """
            INSERT INTO users (email_id)
            VALUES (%s)
            RETURNING user_id, email_id, created_at;
            """,
            (user.email_id,)
        )

        row = cursor.fetchone()

        connection.commit()

        return {
            "user_id": row[0],
            "email_id": row[1],
            "created_at": row[2]
        }

    except UniqueViolation:
        connection.rollback()

        raise HTTPException(
            status_code=409,
            detail="A user with this email already exists."
        )

    finally:
        cursor.close()
        connection.close()

def get_users():
    connection = get_connection()
    cursor = connection.cursor()

    try:
        cursor.execute(
            """
            SELECT user_id, email_id, created_at
            FROM users
            ORDER BY created_at;
            """
        )

        rows = cursor.fetchall()

        users = []

        for row in rows:
            users.append({
                "user_id": row[0],
                "email_id": row[1],
                "created_at": row[2]
            })

        return users

    finally:
        cursor.close()
        connection.close()

