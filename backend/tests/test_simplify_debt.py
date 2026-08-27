from app.modules.settlements.debt import simplify_debts


def test_simple_debt():
    balances = {
        "Alice": 10000,
        "Bob": -3000,
        "Charlie": -7000,
    }

    result = simplify_debts(balances)

    assert result == [
        {
            "payer_id": "Bob",
            "receiver_id": "Alice",
            "amount": 3000,
        },
        {
            "payer_id": "Charlie",
            "receiver_id": "Alice",
            "amount": 7000,
        },
    ]

def test_multiple_creditors_and_debtors():
    balances = {
        "Alice": 10000,
        "Bob": 5000,
        "Charlie": -8000,
        "Dave": -7000,
    }

    result = simplify_debts(balances)

    assert result == [
        {
            "payer_id": "Charlie",
            "receiver_id": "Alice",
            "amount": 8000,
        },
        {
            "payer_id": "Dave",
            "receiver_id": "Alice",
            "amount": 2000,
        },
        {
            "payer_id": "Dave",
            "receiver_id": "Bob",
            "amount": 5000,
        },
    ]

def test_all_balances_zero():
    balances = {
        "Alice": 0,
        "Bob": 0,
        "Charlie": 0,
    }

    result = simplify_debts(balances)

    assert result == []

import pytest


def test_invalid_balance_sum():
    balances = {
        "Alice": 10000,
        "Bob": -3000,
    }

    with pytest.raises(ValueError):
        simplify_debts(balances)