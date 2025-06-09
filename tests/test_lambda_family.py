import pytest
from typing import Callable
from runnable_family.lambda_family import (
    RunnablePartialLambda,
    RunnableUnpackLambda,
    RunnableDictUnpackLambda,
)


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
    'input_obj, func, expected',
    [
        (
            [1, 2, 3],
            lambda x, y, z: (x + y, z),
            (3, 3)
        ),
        (
            ('a', 'b', 'c'),
            lambda x, y, z: (x + y + z, x),
            ('abc', 'a')
        )
    ]
)
def test_runnable_unpack_lambda(
    input_obj: list | tuple,
    func: Callable[..., tuple[int | str, int | str]],
    expected: tuple[int | str, int | str],
    mocker,
) -> None:
    mock_func = mocker.MagicMock(side_effect=func)
    unpack_lambda = RunnableUnpackLambda(mock_func)  # type: ignore
    assert unpack_lambda.invoke(input_obj) == expected
    mock_func.assert_called_once_with(*input_obj)


@pytest.mark.parametrize(
    'input_obj, func, expected',
    [
        (
            {'x': 1, 'y': 2, 'z': 3},
            lambda x, y, z: (x + y, z),
            (3, 3)
        ),
        (
            {'x': 'a', 'y': 'b', 'z': 'c'},
            lambda x, y, z: (x + y + z, x),
            ('abc', 'a')
        )
    ]
)
def test_runnable_dict_unpack_lambda(
    input_obj: dict[str, int | str],
    func: Callable[..., tuple[int | str, int | str]],
    expected: tuple[int | str, int | str],
    mocker,
) -> None:
    mock_func = mocker.MagicMock(side_effect=func)
    unpack_lambda = RunnableDictUnpackLambda(mock_func)  # type: ignore
    assert unpack_lambda.invoke(input_obj) == expected
    mock_func.assert_called_once_with(**input_obj)
