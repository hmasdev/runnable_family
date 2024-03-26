from langchain_core.runnables import (
    Runnable,
    RunnableBranch,
    RunnableLambda,
    RunnablePassthrough,
)
import pytest
from runnable_family.self_refine import RunnableSelfRefine


@pytest.mark.parametrize(
    "runnable, feedback, refine, input_obj, expected",
    [
        (
            RunnableLambda(lambda i: i+1),
            RunnableLambda(lambda io: tuple(io.values())),
            RunnableLambda(lambda iof: tuple(iof.values())),
            1,
            (
                1,  # Input
                2,  # Output
                (1, 2),  # Feedback
            ),
        ),
        (
            RunnableLambda(lambda question: question),
            RunnablePassthrough().pick('output') | RunnableLambda(lambda s: s.endswith('?')),  # noqa
            RunnableBranch(
                (
                    RunnablePassthrough().pick('feedback'),
                    RunnablePassthrough().pick('output'),
                ),
                RunnableLambda(lambda dic: dic['output']+'?')
            ),
            'What is your name',
            'What is your name?',
        ),
        (
            RunnableLambda(lambda question: question),
            RunnablePassthrough().pick('output') | RunnableLambda(lambda s: s.endswith('?')),  # noqa
            RunnableBranch(
                (
                    RunnablePassthrough().pick('feedback'),
                    RunnablePassthrough().pick('output'),
                ),
                RunnableLambda(lambda dic: dic['output']+'?')
            ),
            'What is your name?',
            'What is your name?',
        )
    ],
)
def test_runnable_self_refine(
    runnable: Runnable[int, int],
    feedback: Runnable[dict[str, int], int],
    refine: Runnable[dict[str, int | int | int], int],
    input_obj: int,
    expected: int,
):
    chain = RunnableSelfRefine(runnable, feedback, refine)
    actual = chain.invoke(input_obj)
    assert actual == expected
    assert chain.InputType == runnable.InputType
    assert chain.OutputType == refine.OutputType
