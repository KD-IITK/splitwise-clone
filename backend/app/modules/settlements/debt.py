def simplify_debts(balances: dict) -> list[dict]:
    total = sum(balances.values())
    if total != 0:
        raise ValueError("Balances must sum to zero!")
    
    creditors = []
    debtors = []

    for user_id, balance in balances.items():
        if balance > 0:
            creditors.append({
                "user_id": user_id,
                "amount": balance,
            })
        elif balance < 0:
            debtors.append({
                "user_id": user_id,
                "amount": -balance,
            })

    transactions = []
    i=0
    j=0

    while i < len(debtors) and j < len(creditors):
        debtor = debtors[i]
        creditor = creditors[j]
        amount = min(debtor["amount"], creditor["amount"])
        transactions.append({
            "payer_id": debtor["user_id"],
            "receiver_id": creditor["user_id"],
            "amount": amount,
        })

        debtor["amount"] -= amount
        creditor["amount"] -= amount

        if debtor["amount"] == 0:
            i += 1
        if creditor["amount"] == 0:
            j += 1

    return transactions


def calculate_pairwise_debts(expenses: list[dict]) -> dict:
    pair_balances = {}

    for expense in expenses:
        payer_id = expense["paid_by"]

        for participant in expense["participants"]:
            user_id = participant["user_id"]
            share = participant["share"]

            if user_id == payer_id:
                continue
            key = tuple(sorted([user_id, payer_id]))
            if key not in pair_balances:
                pair_balances[key] = {
                    "first": key[0],
                    "second": key[1],
                    "balance": 0,
                }

            if user_id == key[0]:
                # first user owes second user
                pair_balances[key]["balance"] += share
            else:
                # second user owes first user
                pair_balances[key]["balance"] -= share

    result = {}

    for data in pair_balances.values():
        balance = data["balance"]
        if balance > 0:
            result[(data["first"], data["second"])] = balance
        elif balance < 0:
            result[(data["second"], data["first"])] = -balance

    return result

def apply_settlements_to_pairwise(debts: dict[tuple, int],settlements: list[dict],) -> dict[tuple, int]:
    pair_balances = {}

    # Convert existing debts into signed pair balances.
    for (debtor, creditor), amount in debts.items():
        pair = tuple(sorted([debtor, creditor]))

        if debtor == pair[0]:
            pair_balances[pair] = amount
        else:
            pair_balances[pair] = -amount

    # Apply settlements.
    for settlement in settlements:
        payer_id = settlement["payer_id"]
        receiver_id = settlement["receiver_id"]
        amount = settlement["amount"]

        pair = tuple(sorted([payer_id, receiver_id]))

        if pair not in pair_balances:
            pair_balances[pair] = 0

        if payer_id == pair[0]:
            # First user pays second user.
            # Debt from first → second decreases.
            pair_balances[pair] -= amount
        else:
            # Second user pays first user.
            pair_balances[pair] += amount

    # Convert signed balances back to debts.
    result = {}

    for (user_a, user_b), balance in pair_balances.items():
        if balance > 0:
            result[(user_a, user_b)] = balance

        elif balance < 0:
            result[(user_b, user_a)] = -balance

    return result