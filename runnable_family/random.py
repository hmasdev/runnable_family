from functools import partial
from itertools import accumulate
import operator
import random
from typing import Callable, Iterable
from langchain_core.runnables import (
    Runnable,
    RunnableBranch,
    RunnableLambda,
    RunnableMap,
    RunnablePassthrough,
    RunnablePick,
    RunnableSequence,
)
from langchain_core.runnables.base import Input, Output


class RunnableRandomBranch(RunnableSequence[Input, Output]):
    """Runnable that branches to one of the runnables based on given probabilities.
    This runnable randomly selects one of the provided runnables based on the specified probabilities.
    It is useful for scenarios where you want to randomly choose a runnable to execute,
    such as in a game or simulation where different outcomes are possible based on probabilities.

    Args:
        *runnables: A variable number of runnables or callables that take an input
            and return an output. These are the runnables to be branched.
        probs: An iterable of probabilities corresponding to each runnable.
            If not provided, equal probabilities are assigned to each runnable.
        generate_random_value: A callable that generates a random value between 0 and 1.
            Defaults to `random.random`.

    Attributes:
        _runnables (Iterable[Runnable[Input, Output]]): List of runnables to be branched.
        _cum_probs (list[float]): Cumulative probabilities of the runnables.
        _generate_random_value (Callable[[], float]): Function to generate a random number.
        _allowed_numerical_error: float = 1e-8

    Example:
        >>> from itertools import cycle
        >>> from runnable_family.random import RunnableRandomBranch
        >>> from langchain_core.runnables import RunnableLambda
        >>> def runnable_a(x):
        ...     return f"A: {x}"
        >>> def runnable_b(x):
        ...     return f"B: {x}"
        >>> def runnable_c(x):
        ...     return f"C: {x}"
        >>> branch = RunnableRandomBranch(
        ...     RunnableLambda(runnable_a),
        ...     RunnableLambda(runnable_b),
        ...     RunnableLambda(runnable_c),
        ...     generate_random_value=cycle([0.5, 0.2, 0.4, 0.8, 0.9, 0.01,]).__next__,
        ... )
        >>> result = branch.invoke("test input")
        >>> print(result)
        B: test input
        >>> result = branch.invoke("another input")
        >>> print(result)
        A: another input
        >>> result = branch.invoke("yet another input")
        >>> print(result)
        B: yet another input
    """  # noqa

    _runnables: Iterable[Runnable[Input, Output]]
    """List of runnables to be branched."""

    _cum_probs: list[float]
    """Cumulative probabilities of the runnables."""

    _generate_random_value: Callable[[], float]
    """Function to generate a random number."""

    __allowed_numerical_error: float = 1e-8

    def __init__(
        self,
        *runnables: Runnable[Input, Output] | Callable[[Input], Output],
        probs: Iterable[float] | None = None,
        generate_random_value: Callable[[], float] = random.random,
        allowed_numerical_error: float = 1e-8,
    ):
        # defaults
        if probs is None:
            probs = [1./len(runnables)] * len(runnables)

        # validation
        # check non-negative probabilities
        if any(map(lambda x: x < 0, probs)):
            raise ValueError(f'Probabilities must be non-negative: probs={probs}')  # noqa
        # check the sum of probabilities
        if abs(sum(probs) - 1.0) > allowed_numerical_error:
            # NOTE: the difference is allowed to be within a small numerical error  # noqa
            raise ValueError(f'The sum of probabilities must be 1.0: sum={sum(probs)}')  # noqa

        # adjust the last probability to make the sum 1.0
        probs = list(probs)
        probs[-1] = 1.0 - sum(probs[:-1])

        # set attributes
        self._runnables = [
            runnable
            if isinstance(runnable, Runnable) else
            RunnableLambda(runnable)
            for runnable in runnables
        ]
        self._cum_probs = list(accumulate(probs, func=operator.add))
        self._generate_random_value = generate_random_value
        self.__allowed_numerical_error = allowed_numerical_error

        super().__init__(
            RunnableMap(
                x=RunnablePassthrough(),
                rv=RunnableLambda(lambda _: generate_random_value()),
            ),
            RunnableBranch(
                *[
                    (
                        RunnablePick("rv")
                        | RunnableLambda(partial(self._a_is_ge_0_le_b, b=thresh)),  # noqa
                        RunnablePick("x") | runnable,
                    )
                    for runnable, thresh in zip(self._runnables, self._cum_probs)  # noqa
                ],
                (
                    RunnablePick("rv")
                    | RunnableLambda(
                        lambda x: f'The random number x is out of range [0, 1]: {x=}'  # noqa
                    )
                    | RunnableLambda(self._raise_value_error)
                )
            ),
        )

    @staticmethod
    def _a_is_ge_0_le_b(a: float, b: float) -> bool:
        """Check if a is less than or equal to b."""
        return 0 <= a <= b

    def _raise_value_error(self, msg: str) -> None:
        raise ValueError(msg)
