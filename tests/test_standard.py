import pytest
from runnable_family.standard import (
    RunnableConstant,
)


@pytest.mark.parametrize(
    'input_obj, expected',
    [
        (0, 0),
        ('a', 0),
        ({'a': 1}, 0),
        ({'a': 1}, 1),
    ]
)
def test_runnable_constant(
    input_obj,
    expected,
):
    constant = RunnableConstant(expected)
    assert constant.invoke(input_obj) == expected
