from langchain_core.runnables import (
    Runnable,
    RunnablePassthrough,
    RunnableSequence,
)
from langchain_core.runnables.base import Input, Output
from typing import Generic, TypeVar

InterMediateInput = TypeVar("InterMediateInput", contravariant=True)
InterMediateOutput = TypeVar("InterMediateOutput", covariant=True)


class RunnableSelfTranslate(
    RunnableSequence[Input, Output],
    Generic[Input, Output, InterMediateInput, InterMediateOutput],
):
    """A runnable that implements the Self-Translate Chain methodology.

    This runnable is designed to translate an input into an intermediate
    representation, process it, and then translate it back to the final output.

    Ref. https://arxiv.org/abs/2308.01223

    Args:
        translater: A runnable that translates the input into an intermediate
            representation.
        inverse_translater: A runnable that translates the intermediate
            representation back to the final output.
        runnable: An optional runnable that processes the intermediate
            representation. If not provided, it defaults to a passthrough
            runnable that simply returns the intermediate input as output.
    Example:
        >>> from langchain_core.runnables import RunnableLambda
        >>> from runnable_family.self_translate import RunnableSelfTranslate
        >>> def translater(input):
        ...     return input + " translated"
        >>> def inverse_translater(intermediate):
        ...     return intermediate + " final output"
        >>> def runnable(intermediate):
        ...     return intermediate.upper()
        >>> # Usage 1
        >>> self_translate_runnable = RunnableSelfTranslate(
        ...     translater=RunnableLambda(translater),
        ...     inverse_translater=RunnableLambda(inverse_translater),
        ...     runnable=RunnableLambda(runnable),
        ... )
        >>> result = self_translate_runnable.invoke("test input")
        >>> print(result)
        TEST INPUT TRANSLATED final output
        >>> # Usage 2
        >>> translate_runnable_factory = RunnableSelfTranslate(
        ...     translater=RunnableLambda(translater),
        ...     inverse_translater=RunnableLambda(inverse_translater),
        ... )
        >>> self_translate_runnable2 = translate_runnable_factory.with_runnable(
        ...    RunnableLambda(runnable)
        ... )
        >>> result2 = self_translate_runnable2.invoke("another test input")
        >>> print(result2)
        ANOTHER TEST INPUT TRANSLATED final output
        >>> _for_reference = translate_runnable_factory.invoke("test input")
        >>> print(_for_reference)
        test input translated final output
    """  # noqa

    _translater: Runnable[Input, InterMediateInput]
    _inverse_translater: Runnable[InterMediateOutput, Output]

    def __init__(
        self,
        translater: Runnable[Input, InterMediateInput],
        inverse_translater: Runnable[InterMediateOutput, Output],
        runnable: Runnable[InterMediateInput, InterMediateOutput] | None = None,  # noqa
    ):
        super().__init__(
            translater,
            runnable or RunnablePassthrough(),  # type: ignore
            inverse_translater,
        )
        self._translater = translater
        self._inverse_translater = inverse_translater

    def with_runnable(
        self,
        runnable: Runnable[InterMediateInput, InterMediateOutput],
    ) -> "RunnableSelfTranslate[Input, Output, InterMediateInput, InterMediateOutput]":  # noqa
        return RunnableSelfTranslate(
            self._translater,
            self._inverse_translater,
            runnable,
        )
