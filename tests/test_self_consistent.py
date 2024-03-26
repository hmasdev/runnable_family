from langchain_core.runnables import Runnable, RunnableLambda
import pytest
from typing import Any, Callable, Iterable
from runnable_family.self_consistent import RunnableSelfConsistent


@pytest.mark.parametrize(
    "runnables, aggregate, input_obj, expected",
    [
        (
            [
                RunnableLambda(lambda x: x + 1),
                RunnableLambda(lambda x: x * 2),
            ],
            sum,
            1,
            4,
        ),
        (
            [
                RunnableLambda(lambda x: x + 1),
                RunnableLambda(lambda x: x * 2),
            ],
            RunnableLambda(sum),
            2,
            7,
        ),
    ],
)
def test_runnable_self_consistent(
    runnables: list[Runnable[int, int]],
    aggregate: Runnable[Iterable[int], int] | Callable[[Iterable[int]], int],
    input_obj: int,
    expected: int,
):
    chain = RunnableSelfConsistent(runnables, aggregate)
    actual = chain.invoke(input_obj)
    assert actual == expected
    assert chain.InputType is runnables[0].InputType
    if isinstance(aggregate, Runnable):
        assert chain.OutputType == aggregate.OutputType
    else:
        assert chain.OutputType == Any
