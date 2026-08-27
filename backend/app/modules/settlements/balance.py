def calculate_expense_balances(expenses: list[dict],user_ids: set) -> dict:
    balances = {
        user_id: 0
        for user_id in user_ids
    }

    for expense in expenses:
        payer_id = expense["paid_by"]
        total_amount = expense["total_amount"]
        balances[payer_id] += total_amount

        for participant in expense["participants"]:
            user_id = participant["user_id"]
            share = participant["share"]
            balances[user_id] -= share
    return balances

def apply_settlements(balances: dict, settlements: list[dict]) -> dict:
    balances = balances.copy()
    for settlement in settlements:
        payer_id = settlement["payer_id"]
        receiver_id = settlement["receiver_id"]
        amount = settlement["amount"]
        balances[payer_id] += amount
        balances[receiver_id] -= amount
    return balances


def calculate_group_balances(expenses: list[dict], settlements: list[dict], user_ids: set) -> dict:
    balances = calculate_expense_balances(expenses,user_ids)
    return apply_settlements(balances,settlements)