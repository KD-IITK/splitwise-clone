from uuid import UUID
from fastapi import HTTPException
from app.db import get_connection
from datetime import datetime, timezone
from psycopg.errors import UniqueViolation

def create_invitation(group_id: UUID, inviter_id: UUID, recipient_email: str):
    connection = get_connection()
    cursor = connection.cursor()

    try:
        # Check whether inviter is a member of the group
        cursor.execute(
            """
            SELECT 1
            FROM group_memberships
            WHERE group_id = %s
              AND user_id = %s;
            """,
            (group_id, inviter_id)
        )

        if cursor.fetchone() is None:
            raise HTTPException(
                status_code=403,
                detail="You are not a member of this group."
            )

        # Check whether recipient is already a member
        cursor.execute(
            """
            SELECT 1
            FROM group_memberships gm
            JOIN users u
              ON u.user_id = gm.user_id
            WHERE gm.group_id = %s
              AND u.email_id = %s;
            """,
            (group_id, recipient_email)
        )

        if cursor.fetchone() is not None:
            raise HTTPException(
                status_code=409,
                detail="User is already a member of this group."
            )

        # Create invitation
        cursor.execute(
            """
            INSERT INTO invitations (
                group_id,
                inviter_id,
                recipient_email,
                expiration_date
            )
            VALUES (
                %s, %s, %s, CURRENT_TIMESTAMP + INTERVAL '7 days'
            )
            RETURNING
                invitation_id,
                group_id,
                recipient_email,
                expiration_date,
                status;
            """,
            (
                group_id,
                inviter_id,
                recipient_email
            )
        )

        row = cursor.fetchone()

        connection.commit()

        return {
            "invitation_id": row[0],
            "group_id": row[1],
            "recipient_email": row[2],
            "expiration_date": row[3],
            "status": row[4]
        }

    except HTTPException:
        connection.rollback()
        raise

    except Exception:
        connection.rollback()
        raise

    finally:
        cursor.close()
        connection.close()

def get_invitation(invitation_id: UUID):
    connection = get_connection()
    cursor = connection.cursor()

    try:
        cursor.execute(
            """
            SELECT
                invitation_id,
                group_id,
                inviter_id,
                recipient_email,
                expiration_date,
                status
            FROM invitations
            WHERE invitation_id = %s;
            """,
            (invitation_id,)
        )

        row = cursor.fetchone()
        if row is None:
            raise HTTPException(
                status_code=404,
                detail="Invitation not found."
            )

        return {
            "invitation_id": row[0],
            "group_id": row[1],
            "inviter_id": row[2],
            "recipient_email": row[3],
            "expiration_date": row[4],
            "status": row[5]
        }

    finally:
        cursor.close()
        connection.close()

def accept_invitation(invitation_id: UUID,user_id: UUID,username: str):
    connection = get_connection()
    cursor = connection.cursor()

    now = datetime.now(timezone.utc)
    try:
        # Get invitation
        cursor.execute(
            """
            SELECT
                group_id,
                recipient_email,
                expiration_date,
                status
            FROM invitations
            WHERE invitation_id = %s
            FOR UPDATE;
            """,
            (invitation_id,)
        )
        invitation = cursor.fetchone()

        if invitation is None:
            raise HTTPException(
                status_code=404,
                detail="Invitation not found."
            )

        group_id = invitation[0]
        recipient_email = invitation[1]
        expiration_date = invitation[2]
        status = invitation[3]

        # Check invitation status
        if status != "PENDING":
            raise HTTPException(
                status_code=409,
                detail="Invitation has already been accepted."
            )

        # Check expiration
        if expiration_date <= now:
            raise HTTPException(
                status_code=410,
                detail="Invitation has expired."
            )

        # Get authenticated user's email
        cursor.execute(
            """
            SELECT email_id
            FROM users
            WHERE user_id = %s;
            """,
            (user_id,)
        )

        user = cursor.fetchone()

        if user is None:
            raise HTTPException(
                status_code=401,
                detail="User not found."
            )

        user_email = user[0]

        # Check invited email
        if user_email.lower() != recipient_email.lower():
            raise HTTPException(
                status_code=403,
                detail="This invitation is not for your account."
            )

        # Check existing membership
        cursor.execute(
            """
            SELECT 1
            FROM group_memberships
            WHERE group_id = %s
              AND user_id = %s;
            """,
            (group_id, user_id)
        )

        if cursor.fetchone() is not None:
            raise HTTPException(
                status_code=409,
                detail="You are already a member of this group."
            )

        # Create membership
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

        # Mark invitation as accepted
        cursor.execute(
            """
            UPDATE invitations
            SET status = 'ACCEPTED'
            WHERE invitation_id = %s;
            """,
            (invitation_id,)
        )

        connection.commit()

        return {
            "message": "Invitation accepted successfully.",
            "group_id": group_id,
            "username": username
        }

    except HTTPException:
        connection.rollback()
        raise

    except UniqueViolation:
        connection.rollback()
        raise HTTPException(
            status_code=409,
            detail="Username is already taken in this group."
        )

    except Exception:
        connection.rollback()
        raise

    finally:
        cursor.close()
        connection.close()