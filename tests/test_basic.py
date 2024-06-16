import pytest
from typing import Callable
from runnable_family.basic import (
    RunnableAdd,
    RunnableConstant,
    RunnableLog,
    RunnablePartialLambda,
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


@pytest.mark.parametrize(
    'input_obj, func, kwargs, expected',
    [
        (0, lambda x: x+10, {}, 10),
        ('x', lambda x, a: x + a, {'a': 'A'}, 'xA'),
        ('z', lambda x, a: x + a, {'a': 'A'}, 'zA'),
        ('x', lambda x, a, b: x + a + b, {'a': 'A', 'b': 'B'}, 'xAB'),
    ]
)
def test_runnable_partial_lambda(
    input_obj: str | int,
    func: Callable[[str | int], str | int],
    kwargs: dict[str, str | int],
    expected: str | int,
    mocker,
) -> None:
    mock_func = mocker.MagicMock(side_effect=func)
    partial_lambda = RunnablePartialLambda(mock_func, **kwargs)
    assert partial_lambda.invoke(input_obj) == expected
    mock_func.assert_called_once_with(input_obj, **kwargs)


@pytest.mark.parametrize(
    'input_obj',
    [
        0,
        'a',
        {'a': 1},
    ]
)
def test_runnable_log(
    input_obj,
    mocker,
):
    func = mocker.MagicMock(return_value=None)
    log_runnable = RunnableLog(func)
    log_runnable.invoke(input_obj)
    func.assert_called_once_with(input_obj)
