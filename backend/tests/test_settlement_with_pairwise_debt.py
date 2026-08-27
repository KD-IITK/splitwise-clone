from app.modules.settlements.debt import apply_settlements_to_pairwise
def test_settlement_reduces_pairwise_debt():
    debts = {
        ("Bob", "Alice"): 10000,
    }

    settlements = [
        {
            "payer_id": "Bob",
            "receiver_id": "Alice",
            "amount": 3000,
        }
    ]

    result = apply_settlements_to_pairwise(debts,settlements)

    assert result == {
        ("Bob", "Alice"): 7000,
    }

def test_settlement_overpayment_reverses_debt():
    debts = {
        ("Bob", "Alice"): 10000,
    }

    settlements = [
        {
            "payer_id": "Bob",
            "receiver_id": "Alice",
            "amount": 15000,
        }
    ]

    result = apply_settlements_to_pairwise(debts,settlements)

    assert result == {
        ("Alice", "Bob"): 5000,
    }

def test_reverse_payment_increases_debt():
    debts = {
        ("Bob", "Alice"): 10000,
    }

    settlements = [
        {
            "payer_id": "Alice",
            "receiver_id": "Bob",
            "amount": 3000,
        }
    ]

    result = apply_settlements_to_pairwise(debts,settlements)

    assert result == {
        ("Bob", "Alice"): 13000,
    }