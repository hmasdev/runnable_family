from langchain_core.runnables import (
    Runnable,
    RunnableLambda,
    RunnableParallel,
    RunnableSequence,
)
from langchain_core.runnables.base import Input, Output
from typing import Any


class RunnableGacha(RunnableSequence[Input, list[Output]]):
    """Runnable that runs the same runnable multiple times in parallel.
    This is useful for scenarios where you want to gather multiple outputs
    from the same runnable, such as in a gacha system where you want to
    simulate drawing multiple items or results.

    Here is "Gacha" means "lottery" or "draw" in Japanese, and it is often used
    in the context of games or applications where users can draw random items
    or characters.

    Args:
        runnable: The runnable to run multiple times.
        n: The number of times to run the runnable in parallel.
            Default is 10.
    Attributes:
        _chain (Runnable[Input, Output]): The chain of runnables that runs
            the same runnable `n` times in parallel and collects the results
            into a list.
    Example:
        >>> from runnable_family.gacha import RunnableGacha
        >>> from langchain_core.runnables import RunnableLambda
        >>> def my_runnable(x):
        ...     return x * 2
        >>> gacha_runnable = RunnableGacha(RunnableLambda(my_runnable), n=5)
        >>> results = gacha_runnable.invoke(10)
        >>> print(results)  # Output: [20, 20, 20, 20, 20]
        [20, 20, 20, 20, 20]
        >>> # This will run `my_runnable` 5 times in parallel with input 10
    """

    def __init__(
        self,
        runnable: Runnable[Input, Output],
        n: int = 10,
    ):
        super().__init__(
            RunnableParallel(**{str(i): runnable for i in range(n)}).with_types(input_type=runnable.InputType),  # type: ignore # noqa
            RunnableLambda(lambda dic: dic.values()),
            RunnableLambda(list).with_types(output_type=list[runnable.OutputType]),  # type: ignore # noqa
        )
