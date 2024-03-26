from langchain_core.runnables import RunnableLambda
import pytest
from runnable_family.self_translate import RunnableSelfTranslate


@pytest.mark.parametrize(
    'translater, inverse_translate, runnable, input_obj, expected',
    [
        (
            RunnableLambda(lambda x: x + 1),
            RunnableLambda(lambda x: x - 1),
            RunnableLambda(lambda x: x + 5),
            1,
            6,
        ),
        (
            RunnableLambda(lambda x: x * -1),
            RunnableLambda(lambda x: x * -1),
            RunnableLambda(lambda x: x * 5),
            6,
            30,
        ),
    ]
)
def test_runnable_self_translate(
    translater: RunnableLambda[int, int],
    inverse_translate: RunnableLambda[int, int],
    runnable: RunnableLambda[int, int],
    input_obj: int,
    expected: int,
):
    chain = RunnableSelfTranslate(
        translater,
        inverse_translate,
        runnable,
    )
    actual = chain.invoke(input_obj)
    assert actual == expected


@pytest.mark.parametrize(
    'translater, inverse_translate, runnable, input_obj, expected',
    [
        (
            RunnableLambda(lambda x: x + 1),
            RunnableLambda(lambda x: x - 1),
            RunnableLambda(lambda x: x + 5),
            1,
            6,
        ),
        (
            RunnableLambda(lambda x: x * -1),
            RunnableLambda(lambda x: x * -1),
            RunnableLambda(lambda x: x * 5),
            6,
            30,
        ),
    ]
)
def test_runnable_self_translate_with_runnable(
    translater: RunnableLambda[int, int],
    inverse_translate: RunnableLambda[int, int],
    runnable: RunnableLambda[int, int],
    input_obj: int,
    expected: int,
):
    chain = RunnableSelfTranslate(
        translater,
        inverse_translate,
    )
    actual = chain.with_runnable(runnable).invoke(input_obj)
    assert actual == expected
    assert chain.InputType == translater.InputType
    assert chain.OutputType == inverse_translate.OutputType
