from collections import Counter
from langchain_core.runnables import (
    Runnable,
    RunnableLambda,
    RunnableParallel,
    RunnableSequence,
)
from langchain_core.runnables.base import Input, Output
from typing import Callable, Iterable, TypeVar

InterMediate = TypeVar("InterMediate", covariant=True)


class RunnableSelfConsistent(RunnableSequence[Input, Output]):
    """A runnable that implements the self-consistent approach to aggregate
    the outputs of multiple runnables. It runs the runnables in parallel,
    collects their outputs, and aggregates them using a specified aggregation
    function or runnable. This is useful for scenarios where you want to
    gather multiple outputs from different runnables and then combine them
    into a single output, such as in self-consistent reasoning or ensemble
    methods.
    This runnable is inspired by the self-consistent approach in
    "Self-Consistency Improves Chain of Thought Reasoning in Language Models"
    (https://arxiv.org/abs/2203.11171).

    Args:
        runnables: An iterable of runnables to run in parallel.
        aggregate: A runnable or callable that takes an iterable of
            intermediate outputs and aggregates them into a final output.
            If not provided, it defaults to counting the occurrences of each
            output and returning the most common one.

    Example:
        >>> from langchain_core.runnables import RunnableLambda
        >>> from runnable_family.self_consistent import RunnableSelfConsistent
        >>> def runnable_a(x):
        ...     return x + 1
        >>> def runnable_b(x):
        ...     return x + 2
        >>> def runnable_c(x):
        ...     return x + 1
        >>> runnables = [
        ...     RunnableLambda(runnable_a),
        ...     RunnableLambda(runnable_b),
        ...     RunnableLambda(runnable_c),
        ... ]
        >>> self_consistent_runnable = RunnableSelfConsistent(runnables)
        >>> result = self_consistent_runnable.invoke(10)
        >>> print(result)
        11
    """  # noqa

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

        super().__init__(
            RunnableParallel(**{str(i): runnable for i, runnable in enumerate(runnables)}),  # type: ignore # noqa
            RunnableLambda(dict.values),
            RunnableLambda(list),
            aggregate,
        )
