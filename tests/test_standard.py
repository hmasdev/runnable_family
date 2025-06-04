import pytest
from runnable_family.standard import (
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
    'x, constant, prepend, expected',
    [
        (1, 2, True, 2 + 1),
        (2, 3, False, 2 + 3),
        ('a', 'b', True, 'b' + 'a'),
        ('b', 'c', False, 'b' + 'c'),
    ]
)
def test_runnable_add(
    x: str | int,
    constant: str | int,
    prepend: bool,
    expected: str | int,
):
    assert type(x) is type(constant)
    add_b: RunnableAdd = RunnableAdd(constant, prepend=prepend)
    assert add_b.invoke(x) == expected


def test_runnable_add_with_non_addable():
    with pytest.raises(TypeError):
        RunnableAdd({'a': 1}).invoke({'a': 1})
