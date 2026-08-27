from app.modules.settlements.balance import calculate_expense_balances, apply_settlements

def test_single_equal_expense():
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
    result = calculate_expense_balances(
        expenses,
        {"Alice", "Bob", "Charlie"},
    )
    assert result == {
        "Alice": 8000,
        "Bob": -4000,
        "Charlie": -4000,
    }

def test_settlement():
    balances = {
        "Alice": 8000,
        "Bob": -4000,
        "Charlie": -4000,
    }
    settlements = [
        {
            "payer_id": "Bob",
            "receiver_id": "Alice",
            "amount": 2000,
        }
    ]
    result = apply_settlements(
        balances,
        settlements,
    )
    assert result == {
        "Alice": 6000,
        "Bob": -2000,
        "Charlie": -4000,
    }

def test_overpayment_reverses_balance():
    balances = {
        "Alice": 10000,
        "Bob": -10000,
    }
    settlements = [
        {
            "payer_id": "Alice",
            "receiver_id": "Bob",
            "amount": 15000,
        }
    ]
    result = apply_settlements(
        balances,
        settlements,
    )
    assert result == {
        "Alice": 25000,
        "Bob": -25000,
    }


def test_multiple_expenses():
    expenses = [
        {
            "paid_by": "Alice",
            "total_amount": 12000,
            "participants": [
                {"user_id": "Alice", "share": 4000},
                {"user_id": "Bob", "share": 4000},
                {"user_id": "Charlie", "share": 4000},
            ],
        },
        {
            "paid_by": "Bob",
            "total_amount": 6000,
            "participants": [
                {"user_id": "Alice", "share": 2000},
                {"user_id": "Bob", "share": 2000},
                {"user_id": "Charlie", "share": 2000},
            ],
        },
    ]
    result = calculate_expense_balances(
        expenses,
        {"Alice", "Bob", "Charlie"},
    )
    assert result == {
        "Alice": 6000,
        "Bob": 0,
        "Charlie": -6000,
    }

def test_balances_sum_to_zero():
    balances = {
        "Alice": 8000,
        "Bob": -4000,
        "Charlie": -4000,
    }
    assert sum(balances.values()) == 0

def test_balances_after_settlement_sum_to_zero():
    balances = {
        "Alice": 8000,
        "Bob": -4000,
        "Charlie": -4000,
    }
    settlements = [
        {
            "payer_id": "Bob",
            "receiver_id": "Alice",
            "amount": 2000,
        }
    ]
    result = apply_settlements(
        balances,
        settlements,
    )
    assert sum(result.values()) == 0