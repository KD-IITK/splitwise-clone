from uuid import UUID
from fastapi import HTTPException
from app.db import get_connection
from app.modules.expenses.split import calculate_equal_split, validate_unequal_split
from app.modules.groups.service import get_group_member_ids, is_group_member

def create_expense(group_id: UUID, creator_id: UUID, request):
    # verify creator is a member of the group
    if not is_group_member(group_id, creator_id):
        raise HTTPException(
            status_code=403,
            detail="You are not a member of this group"
        )

    # verify payer is a member
    if not is_group_member(group_id, request.paid_by):
        raise HTTPException(
            status_code=400,
            detail="Payer must be member of the group"
        )

    # get all group members
    group_member_ids = get_group_member_ids(group_id)
    participants_ids = [
        participant.user_id
        for participant in request.participants
    ]

    # verify each participant is group member
    if not all(
        user_id in group_member_ids
        for user_id in participants_ids
    ):
        raise HTTPException(
            status_code=400,
            detail="All participants must be members of the group"
        )

    # calculate / validate share
    try:
        if request.split_method == "EQUAL":
            shares = calculate_equal_split(request.total_amount, participants_ids)
        else:
            shares = validate_unequal_split(
                request.total_amount,
                [
                    {
                        "user_id": participant.user_id,
                        "share": participant.share,
                    }
                    for participant in request.participants
                ]
            )
    except ValueError as error:
        raise HTTPException(
            status_code=400,
            detail=str(error)
        )

    connection = get_connection()
    cursor = connection.cursor()

    try:
        # create expense
        cursor.execute(
            """
            INSERT INTO expenses (group_id, created_by, paid_by, description, total_amount, split_method)
            VALUES (%s, %s, %s, %s, %s, %s)
            RETURNING 
                expense_id,
                group_id,
                created_by,
                paid_by,
                description,
                total_amount,
                split_method,
                created_at
            """,
            (group_id, creator_id, request.paid_by, request.description, request.total_amount, request.split_method)
        )

        expense = cursor.fetchone()

        # create participants
        for participant in shares:
            cursor.execute(
                """
                INSERT INTO expense_participants (
                    expense_id,
                    user_id,
                    share
                )
                VALUES (%s, %s, %s);
                """,
                (
                    expense[0],
                    participant["user_id"],
                    participant["share"],
                )
            )

        connection.commit()

        return {
            "expense_id": expense[0],
            "group_id": expense[1],
            "created_by": expense[2],
            "paid_by": expense[3],
            "description": expense[4],
            "total_amount": expense[5],
            "split_method": expense[6],
            "created_at": expense[7],
        }

    except Exception:
        connection.rollback()
        raise

    finally:
        cursor.close()
        connection.close()

def get_group_expenses(group_id: UUID, user_id: UUID):
    connection = get_connection()
    cursor = connection.cursor()

    try:
        # Check that the requesting user belongs to the group
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

        # Get expenses and participants
        cursor.execute(
            """
            SELECT
                e.expense_id,
                e.group_id,
                e.created_by,
                e.paid_by,
                e.description,
                e.total_amount,
                e.split_method,
                e.created_at,
                ep.user_id,
                ep.share
            FROM expenses e
            LEFT JOIN expense_participants ep
                ON ep.expense_id = e.expense_id
            WHERE e.group_id = %s
            ORDER BY e.created_at DESC;
            """,
            (group_id,)
        )

        rows = cursor.fetchall()
        expenses = {}
        for row in rows:
            expense_id = row[0]

            if expense_id not in expenses:
                expenses[expense_id] = {
                    "expense_id": row[0],
                    "group_id": row[1],
                    "created_by": row[2],
                    "paid_by": row[3],
                    "description": row[4],
                    "total_amount": row[5],
                    "split_method": row[6],
                    "created_at": row[7],
                    "participants": []
                }

            if row[8] is not None:
                expenses[expense_id]["participants"].append({
                    "user_id": row[8],
                    "share": row[9]
                })

        return list(expenses.values())

    finally:
        cursor.close()
        connection.close()

def get_expense(group_id: UUID, expense_id: UUID, user_id: UUID):
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

        # Fetch expense
        cursor.execute(
            """
            SELECT
                expense_id,
                group_id,
                created_by,
                paid_by,
                description,
                total_amount,
                split_method,
                created_at
            FROM expenses
            WHERE expense_id = %s
              AND group_id = %s;
            """,
            (expense_id, group_id)
        )

        expense = cursor.fetchone()

        if expense is None:
            raise HTTPException(
                status_code=404,
                detail="Expense not found."
            )

        # Fetch participants
        cursor.execute(
            """
            SELECT user_id, share
            FROM expense_participants
            WHERE expense_id = %s;
            """,
            (expense_id,)
        )

        participants = cursor.fetchall()

        return {
            "expense_id": expense[0],
            "group_id": expense[1],
            "created_by": expense[2],
            "paid_by": expense[3],
            "description": expense[4],
            "total_amount": expense[5],
            "split_method": expense[6],
            "created_at": expense[7],
            "participants": [
                {
                    "user_id": row[0],
                    "share": row[1]
                }
                for row in participants
            ]
        }

    finally:
        cursor.close()
        connection.close()

def update_expense(group_id: UUID, expense_id: UUID, user_id: UUID, request):
    connection = get_connection()
    cursor = connection.cursor()

    try:
        # Lock the expense while updating it
        cursor.execute(
            """
            SELECT created_by
            FROM expenses
            WHERE expense_id = %s
            AND group_id = %s
            FOR UPDATE
            """,
            (expense_id, group_id)
        )

        expense = cursor.fetchone()

        if expense is None:
            raise HTTPException(
                status_code=404,
                detail="Expense not found"
            )
        #only the creator can edit
        if expense[0] != user_id:
            raise HTTPException(
                status_code=403,
                detail="Only the expense creator can edit this expense"
            )

        cursor.execute(
            """
            SELECT 1
            FROM group_memberships
            WHERE group_id = %s
            AND user_id = %s
            """,
            (group_id, request.paid_by)
        )

        if cursor.fetchone() is None:
            raise HTTPException(
                status_code=400,
                detail="payer must be meber of the group"
            )

        group_member_ids = get_group_member_ids(group_id)
        participant_ids = [
            participant.user_id
            for participant in request.participants
        ]

        if not all(
            participant_id in group_member_ids
            for participant_id in participant_ids
        ):
            raise HTTPException(
                status_code=400,
                detail="All participants must be member of the group."
            )
        # calculate/validate shares
        try:
            if request.split_method == "EQUAL":
                shares = calculate_equal_split(request.total_amount, participant_ids)
            else:
                shares = validate_unequal_split(
                    request.total_amount,
                    [
                        {
                            "user_id": participant.user_id,
                            "share": participant.share
                        }
                        for participant in request.participants
                    ]
                )
        except ValueError as error:
            raise HTTPException(
                status_code=400,
                detail=str(error)
            )

        #update expense
        cursor.execute(
            """
            UPDATE expenses
            SET
                paid_by = %s,
                description = %s,
                total_amount = %s,
                split_method = %s,
                updated_at = CURRENT_TIMESTAMP
            WHERE expense_id = %s
            AND group_id = %s
            RETURNING
                expense_id,
                group_id,
                created_by,
                paid_by,
                description,
                total_amount,
                split_method,
                created_at;
            """,
            (
                request.paid_by,
                request.description,
                request.total_amount,
                request.split_method,
                expense_id,
                group_id,
            )
        )

        updated_expense = cursor.fetchone()

        # remove old participants
        cursor.execute(
            """
            DELETE FROM expense_participants
            WHERE expense_id = %s
            """,
            (expense_id,)
        )
        # inser new participants
        for participant in shares:
            cursor.execute(
                """
                INSERT INTO expense_participants(
                    expense_id,
                    user_id,
                    share
                )
                VALUES (%s, %s, %s)
                """,
                (
                    expense_id, 
                    participant["user_id"], 
                    participant["share"]
                )
            )

        connection.commit()
        return {
            "expense_id": updated_expense[0],
            "group_id": updated_expense[1],
            "created_by": updated_expense[2],
            "paid_by": updated_expense[3],
            "description": updated_expense[4],
            "total_amount": updated_expense[5],
            "split_method": updated_expense[6],
            "created_at": updated_expense[7],
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

def delete_expense(group_id: UUID, expense_id: UUID, user_id: UUID):
    connection = get_connection()
    cursor = connection.cursor()

    try:
        cursor.execute(
            """
            SELECT created_by
            FROM expenses
            WHERE expense_id = %s
            AND group_id = %s
            FOR UPDATE;
            """,
            (expense_id, group_id)
        )

        expense = cursor.fetchone()

        if expense is None:
            raise HTTPException(
                status_code=404,
                detail="Expense not found."
            )

        if expense[0] != user_id:
            raise HTTPException(
                status_code=403,
                detail="Only the expense creator can delete this expense."
            )

        cursor.execute(
            """
            DELETE FROM expenses
            WHERE expense_id = %s
            AND group_id = %s;
            """,
            (expense_id, group_id)
        )

        connection.commit()

        return {
            "message": "Expense deleted successfully."
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

