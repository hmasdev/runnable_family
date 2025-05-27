import pytest
from typing import Callable
from runnable_family.lambda_family import (
    RunnablePartialLambda,
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
