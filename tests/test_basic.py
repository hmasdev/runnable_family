import pytest
from runnable_family.operator import (
    RunnableAddConstant,
)


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
    add_b: RunnableAddConstant = RunnableAddConstant(constant, prepend=prepend)
    assert add_b.invoke(x) == expected


def test_runnable_add_with_non_addable():
    with pytest.raises(TypeError):
        RunnableAddConstant({'a': 1}).invoke({'a': 1})
