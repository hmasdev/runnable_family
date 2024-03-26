from langchain_core.runnables import (
    Runnable,
    RunnableLambda,
    RunnableParallel,
)
from langchain_core.runnables.base import Input, Output
from typing import Any, Iterable, TypeVar

InterMediate = TypeVar("InterMediate", covariant=True)


class RunnableDiff(Runnable[Input, Output]):
    ''' A simple implementation of Chain To Compare Two Runnables
    '''

    _diff_chain: Runnable[Input, Output]

    def __init__(
        self,
        runnable1: Runnable[Input, InterMediate],
        runnable2: Runnable[Input, InterMediate],
        diff: Runnable[Iterable[InterMediate], Output],
    ):
        self._diff_chain = (
            RunnableParallel(**{
                'output1': runnable1,
                'output2': runnable2,
            })
            | RunnableLambda(dict.values)
            | RunnableLambda(list)
            | diff
        )

    def invoke(self, *args, **kwargs) -> Output:
        # To make it a concrete class
        return self._diff_chain.invoke(*args, **kwargs)

    def __getattribute__(self, name: str) -> Any:
        if name in ["_diff_chain", "invoke"]:
            return super().__getattribute__(name)
        try:
            return getattr(self._diff_chain, name)
        except AttributeError:
            return super().__getattribute__(name)

    @property
    def InputType(self) -> type[Input]:
        return self._diff_chain.InputType

    @property
    def OutputType(self) -> type[Output]:
        return self._diff_chain.OutputType
