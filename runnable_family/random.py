from itertools import accumulate
import operator
import random
from typing import Callable, Iterable
from langchain_core.runnables import Runnable, RunnableLambda
from langchain_core.runnables.base import Input, Output


class RunnableRandomBranch(Runnable[Input, Output]):
    '''Runnable that branches the input to multiple runnables based on random probabilities.

    Args:
        *runnables: runnables to be branched.
        probs: Probabilities of the runnables. If None, equal probabilities are assigned.
        generate_random_value: Function to generate a random number. Default is random.random.
    '''  # noqa

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
    ):
        # defaults
        if probs is None:
            probs = [1./len(runnables)] * len(runnables)

        # validation
        # check non-negative probabilities
        if any(map(lambda x: x < 0, probs)):
            raise ValueError(f'Probabilities must be non-negative: probs={probs}')  # noqa
        # check the sum of probabilities
        if abs(sum(probs) - 1.0) > self.__allowed_numerical_error:
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

    def invoke(self, *args, **kwargs) -> Output:
        x = self._generate_random_value()
        for runnable, thresh in zip(self._runnables, self._cum_probs):
            if 0 <= x <= thresh:
                return runnable.invoke(*args, **kwargs)
        raise ValueError(f'The random number is out of range: random value={x}, cumprod={self._cum_probs}')  # noqa
