from uuid import UUID
from fastapi import HTTPException
from app.db import get_connection
from app.modules.settlements.balance import calculate_group_balances
from app.modules.settlements.debt import calculate_pairwise_debts, apply_settlements_to_pairwise, simplify_debts

def get_group_balances(group_id: UUID, user_id: UUID):
    connection = get_connection()
    cursor = connection.cursor()

    try:
        # Verify requester is a group member
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

        # Get all group members
        cursor.execute(
            """
            SELECT user_id
            FROM group_memberships
            WHERE group_id = %s;
            """,
            (group_id,)
        )

        group_member_ids = {
            row[0]
            for row in cursor.fetchall()
        }

        # Get expenses
        cursor.execute(
            """
            SELECT
                e.expense_id,
                e.paid_by,
                e.total_amount
            FROM expenses e
            WHERE e.group_id = %s;
            """,
            (group_id,)
        )

        expense_rows = cursor.fetchall()
        expenses = []
        for row in expense_rows:
            expense_id = row[0]

            cursor.execute(
                """
                SELECT user_id, share
                FROM expense_participants
                WHERE expense_id = %s;
                """,
                (expense_id,)
            )

            participants = [
                {
                    "user_id": participant[0],
                    "share": participant[1],
                }
                for participant in cursor.fetchall()
            ]

            expenses.append({
                "paid_by": row[1],
                "total_amount": row[2],
                "participants": participants,
            })

        # Get settlements
        cursor.execute(
            """
            SELECT
                payer_id,
                receiver_id,
                amount
            FROM settlements
            WHERE group_id = %s;
            """,
            (group_id,)
        )

        settlements = [
            {
                "payer_id": row[0],
                "receiver_id": row[1],
                "amount": row[2],
            }
            for row in cursor.fetchall()
        ]

        balances = calculate_group_balances(
            expenses=expenses,
            settlements=settlements,
            user_ids=group_member_ids,
        )

        return [
            {
                "user_id": member_id,
                "balance": balance,
            }
            for member_id, balance in balances.items()
        ]

    finally:
        cursor.close()
        connection.close()

def create_settlement(group_id: UUID, user_id: UUID, request):
    connection = get_connection()
    cursor = connection.cursor()

    try:
        # Verify payer is a group member
        cursor.execute(
            """
            SELECT 1
            FROM group_memberships
            WHERE group_id = %s
            AND user_id = %s;
            """,
            (group_id, request.payer_id)
        )

        if cursor.fetchone() is None:
            raise HTTPException(
                status_code=400,
                detail="Payer must be a member of the group."
            )

        # Verify receiver is a group member
        cursor.execute(
            """
            SELECT 1
            FROM group_memberships
            WHERE group_id = %s
            AND user_id = %s;
            """,
            (group_id, request.receiver_id)
        )

        if cursor.fetchone() is None:
            raise HTTPException(
                status_code=400,
                detail="Receiver must be a member of the group."
            )

        # Payer and receiver must be different
        if request.payer_id == request.receiver_id:
            raise HTTPException(
                status_code=400,
                detail="Payer and receiver must be different."
            )

        if (user_id != request.payer_id and user_id != request.receiver_id):
            raise HTTPException(
                status_code=403,
                detail="You must be the payer or receiver."
            )

        # Create settlement
        cursor.execute(
            """
            INSERT INTO settlements (
                group_id,
                payer_id,
                receiver_id,
                amount
            )
            VALUES (%s, %s, %s, %s)
            RETURNING
                settlement_id,
                group_id,
                payer_id,
                receiver_id,
                amount,
                created_at;
            """,
            (
                group_id,
                request.payer_id,
                request.receiver_id,
                request.amount,
            )
        )

        settlement = cursor.fetchone()
        connection.commit()

        return {
            "settlement_id": settlement[0],
            "group_id": settlement[1],
            "payer_id": settlement[2],
            "receiver_id": settlement[3],
            "amount": settlement[4],
            "created_at": settlement[5],
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

def get_group_settlements(group_id: UUID, user_id: UUID):
    connection = get_connection()
    cursor = connection.cursor()

    try:
        # Verify that the requesting user is a group member
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

        cursor.execute(
            """
            SELECT
                settlement_id,
                group_id,
                payer_id,
                receiver_id,
                amount,
                created_at
            FROM settlements
            WHERE group_id = %s
            ORDER BY created_at DESC;
            """,
            (group_id,)
        )

        rows = cursor.fetchall()

        return [
            {
                "settlement_id": row[0],
                "group_id": row[1],
                "payer_id": row[2],
                "receiver_id": row[3],
                "amount": row[4],
                "created_at": row[5],
            }
            for row in rows
        ]

    finally:
        cursor.close()
        connection.close()

def get_pairwise_debts(group_id: UUID,user_id: UUID):
    connection = get_connection()
    cursor = connection.cursor()

    try:
        # Verify group membership
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

        # Get expenses
        cursor.execute(
            """
            SELECT
                expense_id,
                paid_by,
                total_amount
            FROM expenses
            WHERE group_id = %s;
            """,
            (group_id,)
        )

        expense_rows = cursor.fetchall()
        expenses = []

        for row in expense_rows:
            expense_id = row[0]

            cursor.execute(
                """
                SELECT user_id, share
                FROM expense_participants
                WHERE expense_id = %s;
                """,
                (expense_id,)
            )

            participants = [
                {
                    "user_id": participant[0],
                    "share": participant[1],
                }
                for participant in cursor.fetchall()
            ]

            expenses.append({
                "paid_by": row[1],
                "total_amount": row[2],
                "participants": participants,
            })

        # Get settlements
        cursor.execute(
            """
            SELECT
                payer_id,
                receiver_id,
                amount
            FROM settlements
            WHERE group_id = %s;
            """,
            (group_id,)
        )

        settlements = [
            {
                "payer_id": row[0],
                "receiver_id": row[1],
                "amount": row[2],
            }
            for row in cursor.fetchall()
        ]

        debts = calculate_pairwise_debts(expenses)

        debts = apply_settlements_to_pairwise(
            debts,
            settlements,
        )

        return [
            {
                "payer_id": payer_id,
                "receiver_id": receiver_id,
                "amount": amount,
            }
            for (payer_id, receiver_id), amount
            in debts.items()
        ]

    finally:
        cursor.close()
        connection.close()

def get_simplified_debts(group_id: UUID,user_id: UUID):
    balances = get_group_balances(
        group_id=group_id,
        user_id=user_id,
    )

    balance_dict = {
        item["user_id"]: item["balance"]
        for item in balances
    }

    return simplify_debts(balance_dict)