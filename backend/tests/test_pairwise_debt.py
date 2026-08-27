from app.modules.settlements.debt import calculate_pairwise_debts

def test_single_expense_pairwise_debt():
    expenses = [
        {
            "paid_by": "Alice",
            "total_amount": 10000,
            "participants": [
                {
                    "user_id": "Alice",
                    "share": 5000,
                },
                {
                    "user_id": "Bob",
                    "share": 5000,
                },
            ],
        }
    ]
    result = calculate_pairwise_debts(expenses)
    assert result == {
        ("Bob", "Alice"): 5000,
    }

def test_multiple_participants():
    expenses = [
        {
            "paid_by": "Alice",
            "total_amount": 12000,
            "participants": [
                {
                    "user_id": "Alice",
                    "share": 4000,
                },
                {
                    "user_id": "Bob",
                    "share": 4000,
                },
                {
                    "user_id": "Charlie",
                    "share": 4000,
                },
            ],
        }
    ]
    result = calculate_pairwise_debts(expenses)
    assert result == {
        ("Bob", "Alice"): 4000,
        ("Charlie", "Alice"): 4000,
    }

def test_opposite_debts_are_netted():
    expenses = [
        {
            "paid_by": "Alice",
            "total_amount": 10000,
            "participants": [
                {
                    "user_id": "Bob",
                    "share": 10000,
                },
            ],
        },
        {
            "paid_by": "Bob",
            "total_amount": 3000,
            "participants": [
                {
                    "user_id": "Alice",
                    "share": 3000,
                },
            ],
        },
    ]
    result = calculate_pairwise_debts(expenses)
    assert result == {
        ("Bob", "Alice"): 7000,
    }

def test_equal_opposite_debts_cancel():
    expenses = [
        {
            "paid_by": "Alice",
            "total_amount": 10000,
            "participants": [
                {
                    "user_id": "Bob",
                    "share": 10000,
                },
            ],
        },
        {
            "paid_by": "Bob",
            "total_amount": 10000,
            "participants": [
                {
                    "user_id": "Alice",
                    "share": 10000,
                },
            ],
        },
    ]
    result = calculate_pairwise_debts(expenses)
    assert result == {}