from langchain_core.runnables import (
    Runnable,
    RunnableLambda,
    RunnablePassthrough,
)
import pytest
from runnable_family.loopback import (
    RunnableLoopback,
)


def test_runnable_loopback(mocker):
    # prepare
    runnable = RunnableLambda(lambda x: x+1)
    condition = RunnableLambda(lambda x: x < 10)
    loopback = RunnablePassthrough()
    runnable_invoke_spy = mocker.spy(runnable, 'invoke')
    condition_invoke_spy = mocker.spy(condition, 'invoke')
    # loopback_invoke_spy = mocker.spy(loopback, 'invoke')
    # instantiate
    loopback = RunnableLoopback(
        runnable=runnable,
        condition=condition,
        loopback=loopback,
    )
    # run
    input_obj = 0
    expected = 10
    actual = loopback.invoke(input_obj)
    # assert
    assert actual == expected
    assert runnable_invoke_spy.call_count == 10
    assert condition_invoke_spy.call_count == 10
    # assert loopback_invoke_spy.call_count == 9

    assert loopback.InputType == runnable.InputType
    assert loopback.OutputType == runnable.OutputType

    # check whether get_graph can be called
    loopback.get_graph()


def test_runnable_loopback_with_callable_condition(mocker):
    # prepare
    runnable = RunnableLambda(lambda x: x+1)
    condition = mocker.Mock(side_effect=lambda x: x < 10)
    loopback = RunnablePassthrough()
    runnable_invoke_spy = mocker.spy(runnable, 'invoke')
    condition_invoke_spy = condition
    # loopback_invoke_spy = mocker.spy(loopback, 'invoke')
    # instantiate
    loopback = RunnableLoopback(
        runnable=runnable,
        condition=condition,
        loopback=loopback,
    )
    # run
    input_obj = 0
    expected = 10
    actual = loopback.invoke(input_obj)
    # assert
    assert actual == expected
    assert runnable_invoke_spy.call_count == 10
    assert condition_invoke_spy.call_count == 10
    # assert loopback_invoke_spy.call_count == 9

    assert loopback.InputType == runnable.InputType
    assert loopback.OutputType == runnable.OutputType

    # check whether get_graph can be called
    loopback.get_graph()


@pytest.mark.parametrize(
    'n, input_obj, expected',
    [
        (0, 0, 0),
        (1, 0, 1),
        (2, 0, 2),
        (3, 0, 3),
        (3, -1, 2),
    ]
)
def test_runnable_loopback_with_n_loop(
    n: int,
    input_obj: int,
    expected: int,
    mocker,
):
    # prepare
    runnable = RunnableLambda(lambda x: x+1)
    loopback: Runnable[int, int] = RunnablePassthrough()
    runnable_invoke_spy = mocker.spy(runnable, 'invoke')
    # loopback_invoke_spy = mocker.spy(loopback, 'invoke')
    # instantiate
    loopback = RunnableLoopback.with_n_loop(
        n=n,
        runnable=runnable,
        loopback=loopback,
    )
    # run
    actual = loopback.invoke(input_obj)
    # assert
    assert actual == expected
    assert runnable_invoke_spy.call_count == n
    # assert loopback_invoke_spy.call_count == n-1

    # check whether get_graph can be called
    loopback.get_graph()
