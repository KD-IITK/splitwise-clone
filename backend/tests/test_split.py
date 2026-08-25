from app.modules.expenses.split import calculate_equal_split, validate_unequal_split
import pytest

# equal split tests
def test_equal_split_even():
    result = calculate_equal_split(12000, ["A", "B", "C"]);
    assert result == [
        {"user_id": "A", "share": 4000},
        {"user_id": "B", "share": 4000},
        {"user_id": "C", "share": 4000},
    ]

def test_equal_split_with_remainder():
    result = calculate_equal_split(100, ["A", "B", "C"]);
    assert result == [
        {"user_id": "A", "share": 34},
        {"user_id": "B", "share": 33},
        {"user_id": "C", "share": 33},
    ]

def test_equal_split_rejects_zero_amount():
    with pytest.raises(ValueError):
        calculate_equal_split(0, ["A", "B"])

def test_equal_split_rejects_duplicate_participants():
    with pytest.raises(ValueError):
        calculate_equal_split(10000, ["A", "A", "B"])

def test_equal_split_sum_matches_total():
    result = calculate_equal_split(10001, ["A", "B", "C", "D", "E", "F"])
    total = sum(participant["share"] for participant in result)
    assert total == 10001

# unequal split tests
def test_unequal_split():
    participants = [
        {"user_id": "A", "share": 5000},
        {"user_id": "B", "share": 6000},
        {"user_id": "C", "share": 7000},
    ]

    result = validate_unequal_split(18000, participants)
    assert result == participants

def test_unequal_split_rejects_wrong_total():
    participants = [
        {"user_id": "A", "share": 5000},
        {"user_id": "B", "share": 3000},
    ]
    with pytest.raises(ValueError):
        validate_unequal_split(10000, participants)

def test_unequal_split_rejects_zero_share():
    participants = [
        {"user_id": "A", "share": 10000},
        {"user_id": "B", "share": 0},
    ]
    with pytest.raises(ValueError):
        validate_unequal_split(10000, participants)

def test_unequal_split_rejects_duplicate_users():
    participants = [
        {"user_id": "A", "share": 5000},
        {"user_id": "A", "share": 5000},
    ]

    with pytest.raises(ValueError):
        validate_unequal_split(10000, participants)

