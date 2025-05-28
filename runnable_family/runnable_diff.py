from langchain_core.runnables import (
    Runnable,
    RunnableLambda,
    RunnableParallel,
    RunnableSequence,
)
from langchain_core.runnables.base import Input, Output
from typing import Iterable, TypeVar

InterMediate = TypeVar("InterMediate", covariant=True)


class RunnableDiff(RunnableSequence[Input, Output]):
    """
    A runnable that computes the difference between the outputs of two
    runnables. It runs two runnables in parallel and then applies a
    diff function to their outputs.

    Args:
        runnable1: The first runnable to run.
        runnable2: The second runnable to run.
        diff: A runnable or callable that takes two outputs and computes
            the difference between them. It should accept an iterable of
            two intermediate outputs and return the final output.
    Example:
        >>> from runnable_family.runnable_diff import RunnableDiff
        >>> from langchain_core.runnables import RunnableLambda, RunnableParallel
        >>> def runnable1(x):
        ...     return x + 1
        >>> def runnable2(x):
        ...     return x + 2
        >>> def diff(outputs):
        ...     return outputs[0] - outputs[1]
        >>> diff_runnable = RunnableDiff(
        ...    runnable1=RunnableLambda(runnable1),
        ...    runnable2=RunnableLambda(runnable2),
        ...    diff=RunnableLambda(diff)
        ... )
        >>> result = diff_runnable.invoke(10)
        >>> print(result)
        -1
    """  # noqa

    def __init__(
        self,
        runnable1: Runnable[Input, InterMediate],
        runnable2: Runnable[Input, InterMediate],
        diff: Runnable[Iterable[InterMediate], Output],
    ):
        super().__init__(
            RunnableParallel(**{  # type: ignore
                'output1': runnable1,
                'output2': runnable2,
            }),
            RunnableLambda(dict.values),
            RunnableLambda(list),
            diff,
        )
