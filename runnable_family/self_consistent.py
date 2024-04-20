from collections import Counter
from langchain_core.runnables import (
    Runnable,
    RunnableLambda,
    RunnableParallel,
)
from langchain_core.runnables.base import Input, Output
from typing import Any, Callable, Iterable, TypeVar

InterMediate = TypeVar("InterMediate", covariant=True)


class RunnableSelfConsistent(Runnable[Input, Output]):
    ''' A simple implementation of Self-Consistent Chain as described in the paper:

    Ref. https://arxiv.org/pdf/2203.11171.pdf

    Args:
        runnables: Iterable[Runnable[Input, InterMediate]]: A list of runnables
        aggregate: Runnable[Iterable[InterMediate], Output] | Callable[[Iterable[InterMediate]], Output]:
            A runnable or a callable to aggregate the output of the runnables.
            Default is to count the most common output.
            If there are the most common outputs, the first one is returned,
            e.g. 1 is returned for the runnables' output [0, 1, 1, 2, 2].
    '''  # noqa

    _self_consistent_chain: Runnable[Input, Output]

    def __init__(
        self,
        runnables: Iterable[Runnable[Input, InterMediate]],
        aggregate: Runnable[Iterable[InterMediate], Output] | Callable[[Iterable[InterMediate]], Output] = (  # noqa
            RunnableLambda(Counter)  # type: ignore
            | RunnableLambda(lambda counter: counter.most_common())
            | RunnableLambda(lambda most_common: most_common[0][0])
        )
    ):
        if callable(aggregate):
            aggregate = RunnableLambda(aggregate)
        self._self_consistent_chain = (
            RunnableParallel(**{str(i): runnable for i, runnable in enumerate(runnables)})  # type: ignore # noqa
            | RunnableLambda(dict.values)
            | RunnableLambda(list)
            | aggregate
        )

    def invoke(self, *args, **kwargs) -> Output:
        # To make it a concrete class
        return self._self_consistent_chain.invoke(*args, **kwargs)

    def __getattribute__(self, name: str) -> Any:
        if name in ["_self_consistent_chain", "invoke"]:
            return super().__getattribute__(name)
        try:
            return getattr(self._self_consistent_chain, name)
        except AttributeError:
            return super().__getattribute__(name)

    @property
    def InputType(self) -> type[Input]:
        return self._self_consistent_chain.InputType

    @property
    def OutputType(self) -> type[Output]:
        return self._self_consistent_chain.OutputType
