def calculate_equal_split(total_amount: int, participant_ids: list) -> list[dict]:
    if total_amount <= 0:
        raise ValueError("Total amount must be greater than 0")

    if len(participant_ids) != len(set(participant_ids)):
        raise ValueError("Duplicate participants are not allowed")

    base_share = total_amount // len(participant_ids);
    remainder = total_amount % len(participant_ids);

    shares = []

    for index, user_id in enumerate(participant_ids):
        share = base_share

        if index < remainder:
            share += 1

        shares.append({
            "user_id": user_id,
            "share": share,
        })

    return shares

def validate_unequal_split(total_amount: int, participants: list[dict]) -> list[dict]:
    if total_amount <= 0:
        raise ValueError("Total amount must be greater than 0")

    user_ids = [participant["user_id"] for participant in participants]

    if len(user_ids) != len(set(user_ids)):
        raise ValueError("Duplicate participants are not allowed")

    total_share = 0

    for participant in participants:
        share = participant["share"]
        if share <= 0:
            raise ValueError("Each share must be greater than 0")

        total_share += share

    if total_share != total_amount:
        raise ValueError("total amount must be equal to sum of individual shares")

    return participants