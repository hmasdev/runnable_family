from typing import Callable
from langchain_core.runnables import Runnable, RunnableLambda
import pytest
from runnable_family.random import RunnableRandomBranch


runnables: list[Runnable[int, int] | Callable[[int], int]] = [
    RunnableLambda(lambda x: x + 0),
    RunnableLambda(lambda x: x + 1),
    lambda x: x + 2,
    RunnableLambda(lambda x: x + 3),
]


@pytest.mark.parametrize(
    'random_value, expected',
    [
        (0.0, 0),
        (0.1, 0),
        (0.25, 0),
        (0.3, 1),
        (0.5, 1),
        (0.6, 2),
        (0.75, 2),
        (0.9, 3),
        (1.0, 3),
    ]
)
def test_runnable_random_branch(
    random_value: float,
    expected: int,
):
    chain = RunnableRandomBranch(
        *runnables,
        generate_random_value=lambda: random_value,
    )
    assert chain.invoke(0) == expected
    assert chain.invoke(1) == expected + 1


@pytest.mark.parametrize(
    'probs, random_value, expected',
    [
        ([0.25, 0.5, 0, 0.25], 0.0, 0),
        ([0.25, 0.5, 0, 0.25], 0.1, 0),
        ([0.25, 0.5, 0, 0.25], 0.25, 0),
        ([0.25, 0.5, 0, 0.25], 0.3, 1),
        ([0.25, 0.5, 0, 0.25], 0.5, 1),
        ([0.25, 0.5, 0, 0.25], 0.6, 1),
        ([0.25, 0.5, 0, 0.25], 0.75, 1),
        ([0.25, 0.5, 0, 0.25], 0.9, 3),
        ([0.25, 0.5, 0, 0.25], 1.0, 3),
    ]
)
def test_runnable_random_branch_with_probs(
    probs: list[float],
    random_value: float,
    expected: int,
):
    chain = RunnableRandomBranch(
        *runnables,
        probs=probs,
        generate_random_value=lambda: random_value,
    )
    assert chain.invoke(0) == expected
    assert chain.invoke(1) == expected + 1


@pytest.mark.parametrize(
    'probs',
    [
        [0.1, 0.2, 0.3],  # sum = 0.6
        [0.1, 0.2, 0.3, 0.4, 0.5],  # sum = 1.5
    ]
)
def test_runnable_random_branch_with_invalid_probs(
    probs: list[float],
):
    with pytest.raises(ValueError):
        RunnableRandomBranch(*runnables, probs=probs)


@pytest.mark.parametrize(
    'random_value',
    [
        -0.1,
        1.1,
    ]
)
def test_runnable_random_branch_with_invalid_random_value(
    random_value: float,
):
    chain = RunnableRandomBranch(
        *runnables,
        generate_random_value=lambda: random_value,
    )
    with pytest.raises(ValueError):
        chain.invoke(0)


@pytest.mark.parametrize(
    'probs',
    [
        [-0.1, 0.2, 0.3, 0.6],
        [0.1, -0.2, 0.3, 0.8],
        [0.1, 0.2, -0.3, 1.0],
    ]
)
def test_runnable_random_branch_with_negative_probability(probs: list[float]):  # noqa
    # check if the sum of probabilities is 1.0
    assert sum(probs) == 1.0
    # run test
    with pytest.raises(ValueError):
        RunnableRandomBranch(*runnables, probs=probs)
