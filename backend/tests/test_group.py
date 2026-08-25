import pytest
from fastapi import HTTPException
from uuid import UUID
from app.modules.groups.service import is_group_member, get_group_member_ids

def test_is_group_member():
    group_id = UUID('a7dce6fc-6486-466e-bb52-991fada0da27')
    user_id1 = UUID('3f84e13d-0264-4b3a-9bcd-6f2881e59f17')
    user_id2 = UUID('29367ae9-d7e0-4878-a970-737d378453ba')
    result = [is_group_member(group_id, user_id1), is_group_member(group_id, user_id2)]
    assert result == [True, False]

def test_get_group_member_ids():
    group_id = UUID('a7dce6fc-6486-466e-bb52-991fada0da27')
    expected_members = {
        UUID('3f84e13d-0264-4b3a-9bcd-6f2881e59f17'),
        UUID('94ecdf63-97c9-41b6-90af-ae1f4258f66c'),
        UUID('65b396ac-678e-40f7-8654-be77af4cf646')
    }

    result = get_group_member_ids(group_id)

    assert result == expected_members