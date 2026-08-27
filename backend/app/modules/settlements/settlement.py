def apply_settlement(balance: int, payer_is_a: bool, amount: int) -> int:
    if amount <= 0:
        raise ValueError(
            "Settlement amount must be greater than 0."
        )

    if payer_is_a:
        return balance - amount

    return balance + amount