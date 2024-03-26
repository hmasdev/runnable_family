from langchain_core.runnables import (
    Runnable,
    RunnablePassthrough
)
from langchain_core.runnables.base import Input, Output
from typing import Generic, TypeVar

InterMediateInput = TypeVar("InterMediateInput", contravariant=True)
InterMediateOutput = TypeVar("InterMediateOutput", covariant=True)


class RunnableSelfTranslate(
    Runnable[Input, Output],
    Generic[Input, Output, InterMediateInput, InterMediateOutput],
):
    '''A simple implementation of Self-Translate Chain as described in the paper:

    Ref. https://arxiv.org/abs/2308.01223
    '''  # noqa

    _translater: Runnable[Input, InterMediateInput]
    _inverse_translater: Runnable[InterMediateOutput, Output]
    _runnable: Runnable[InterMediateInput, InterMediateOutput]

    def __init__(
        self,
        translater: Runnable[Input, InterMediateInput],
        inverse_translater: Runnable[InterMediateOutput, Output],
        runnable: Runnable[InterMediateInput, InterMediateOutput] | None = None,  # noqa
    ):
        self._runnable = runnable or RunnablePassthrough()    # type: ignore
        self._translater = translater
        self._inverse_translater = inverse_translater

    def invoke(self, input: Input, *args, **kwargs) -> Output:
        # To make it a concrete class
        return (
            self._translater
            | self._runnable
            | self._inverse_translater
        ).invoke(input, *args, **kwargs)

    def with_runnable(
        self,
        runnable: Runnable[InterMediateInput, InterMediateOutput],
    ) -> Runnable[Input, Output]:
        return RunnableSelfTranslate(
            self._translater,
            self._inverse_translater,
            runnable,
        )

    @property
    def InputType(self) -> type[Input]:
        return self._translater.InputType

    @property
    def OutputType(self) -> type[Output]:
        return self._inverse_translater.OutputType
