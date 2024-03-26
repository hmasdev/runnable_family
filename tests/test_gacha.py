from langchain_core.runnables import RunnableLambda
import pytest
from runnable_family.gacha import RunnableGacha


@pytest.mark.parametrize(
    'runnable, n, input_obj, expected',
    [
        (
            RunnableLambda(lambda x: x + 1),
            2,
            1,
            [2, 2],
        ),
        (
            RunnableLambda(lambda x: x * -1),
            3,
            -1,
            [1, 1, 1],
        ),
    ]
)
def test_runnable_gacha(
    runnable: RunnableLambda[int, int],
    n: int,
    input_obj: int,
    expected: int,
    mocker,
):
    invoke_spy = mocker.spy(runnable, 'invoke')
    chain = RunnableGacha(runnable, n)
    actual = chain.invoke(input_obj)
    assert actual == expected
    assert invoke_spy.call_count == n
    assert chain.InputType == runnable.InputType
    assert chain.OutputType == list[runnable.OutputType]  # type: ignore
