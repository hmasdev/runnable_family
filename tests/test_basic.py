import pytest
from runnable_family.basic import (
    RunnableAdd,
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


@pytest.mark.parametrize(
    'a, b, left, expected',
    [
        (1, 2, True, 3),
        (2, 3, False, 5),
        ('a', 'b', True, 'ab'),
        ('b', 'c', False, 'cb'),
    ]
)
def test_runnable_add(
    a: str | int,
    b: str | int,
    left: bool,
    expected: str | int,
):
    assert type(a) is type(b)
    add_b: RunnableAdd = RunnableAdd(b, left=left)
    assert add_b.invoke(a) == expected


def test_runnable_add_with_non_addable():
    with pytest.raises(TypeError):
        RunnableAdd({'a': 1}).invoke({'a': 1})
