from app.modules.settlements.settlement import apply_settlement
import pytest

def test_a_pays_b():
    result = apply_settlement(
        balance=10000,
        payer_is_a=True,
        amount=3000
    )
    assert result == 7000

def test_b_pays_a():
    result = apply_settlement(
        balance=10000,
        payer_is_a=False,
        amount=3000
    )
    assert result == 13000

def test_a_overpays_b():
    result = apply_settlement(
        balance=10000,
        payer_is_a=True,
        amount=15000
    )
    assert result == -5000

def test_zero_settlement_rejected():
    with pytest.raises(ValueError):
        apply_settlement(
            balance=10000,
            payer_is_a=True,
            amount=0
        )

def test_negative_settlement_rejected():
    with pytest.raises(ValueError):
        apply_settlement(
            balance=10000,
            payer_is_a=True,
            amount=-100
        )

def test_a_pays_b_from_zero():
    result = apply_settlement(
        balance=0,
        payer_is_a=True,
        amount=5000
    )
    assert result == -5000