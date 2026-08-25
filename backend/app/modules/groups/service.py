from uuid import UUID
from app.db import get_connection
from fastapi import HTTPException

def create_group(group_name: str, user_id: UUID, username: str):
    connection = get_connection()
    cursor = connection.cursor()

    try:
        cursor.execute(
            """
            INSERT INTO groups (group_name)
            VALUES (%s)
            RETURNING group_id, group_name, created_at;
            """,
            (group_name,)
        )

        group = cursor.fetchone()
        group_id = group[0]
        cursor.execute(
            """
            INSERT INTO group_memberships (
                user_id,
                group_id,
                username
            )
            VALUES (%s, %s, %s);
            """,
            (user_id, group_id, username)
        )
        connection.commit()
        return {
            "group_id": group[0],
            "group_name": group[1],
            "created_at": group[2]
        }

    except Exception:
        connection.rollback()
        raise

    finally:
        cursor.close()
        connection.close()

def get_user_groups(user_id: UUID):
    connection = get_connection()
    cursor = connection.cursor()

    try:
        cursor.execute(
            """
            SELECT
                g.group_id,
                g.group_name,
                gm.username
            FROM groups g
            JOIN group_memberships gm
                ON gm.group_id = g.group_id
            WHERE gm.user_id = %s
            ORDER BY g.created_at DESC;
            """,
            (user_id,)
        )

        rows = cursor.fetchall()

        return [
            {
                "group_id": row[0],
                "group_name": row[1],
                "username": row[2]
            }
            for row in rows
        ]

    finally:
        cursor.close()
        connection.close()

def get_group_details(group_id: UUID, user_id: UUID):
    connection = get_connection()
    cursor = connection.cursor()

    try:
        # Verify that the requesting user is a member
        cursor.execute(
            """
            SELECT 1
            FROM group_memberships
            WHERE group_id = %s
              AND user_id = %s;
            """,
            (group_id, user_id)
        )

        if cursor.fetchone() is None:
            raise HTTPException(
                status_code=403,
                detail="You are not a member of this group."
            )

        # Get group information
        cursor.execute(
            """
            SELECT group_id, group_name
            FROM groups
            WHERE group_id = %s;
            """,
            (group_id,)
        )

        group = cursor.fetchone()

        if group is None:
            raise HTTPException(
                status_code=404,
                detail="Group not found."
            )

        # Get members
        cursor.execute(
            """
            SELECT user_id, username
            FROM group_memberships
            WHERE group_id = %s
            ORDER BY username;
            """,
            (group_id,)
        )

        members = cursor.fetchall()

        return {
            "group_id": group[0],
            "group_name": group[1],
            "members": [
                {
                    "user_id": member[0],
                    "username": member[1]
                }
                for member in members
            ]
        }

    finally:
        cursor.close()
        connection.close()

def is_group_member(group_id: UUID, user_id: UUID) -> bool:
    connection = get_connection()
    cursor = connection.cursor()
    try:
        cursor.execute(
            """
                SELECT 1
                FROM group_memberships
                WHERE group_id = %s
                AND user_id = %s;
            """,
                (group_id, user_id)
        )

        if cursor.fetchone() is None:
            return False

        return True
    finally:
        cursor.close()
        connection.close()

def get_group_member_ids(group_id: UUID) -> set[UUID]:
    connection = get_connection()
    cursor = connection.cursor()
    try:
        cursor.execute(
            """
                SELECT user_id
                FROM group_memberships
                WHERE group_id = %s;
            """,
            (group_id,)
        )

        rows = cursor.fetchall()
        return {row[0] for row in rows}
    finally:
        cursor.close()
        connection.close()

