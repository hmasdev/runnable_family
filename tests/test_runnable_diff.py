from langchain_core.runnables import RunnableLambda
import pytest
from typing import Iterable
from runnable_family.runnable_diff import RunnableDiff


@pytest.mark.parametrize(
    'runnable1, runnable2, diff, input_obj, expected',
    [
        (
            RunnableLambda(lambda x: x + 1),
            RunnableLambda(lambda x: x - 1),
            RunnableLambda(lambda lst: lst[0] - lst[1]),
            1,
            2,
        ),
        (
            RunnableLambda(lambda x: x * -1),
            RunnableLambda(lambda x: x * -1),
            RunnableLambda(lambda lst: lst[0]/lst[1]),
            2,
            1,
        ),
    ]
)
def test_runnable_diff(
    runnable1: RunnableLambda[int, int],
    runnable2: RunnableLambda[int, int],
    diff: RunnableLambda[Iterable[int], int],
    input_obj: int,
    expected: int,
):
    chain = RunnableDiff(runnable1, runnable2, diff)
    actual = chain.invoke(input_obj)
    assert actual == expected
    assert chain.InputType == runnable1.InputType
    assert chain.OutputType == diff.OutputType
