from functools import partial
import logging
from typing import Callable, TypeVar
from langchain_core.runnables import RunnableLambda

T = TypeVar("T")


class RunnableLog(RunnableLambda[T, T]):
    """Runnable that logs the input and returns it unchanged.

    Args:
        output_func: A callable that takes the input and logs it.
            Defaults to `logging.info`.
        **kwargs: Additional keyword arguments to pass to the base class.

    Example:
        >>> from runnable_family.print_family import RunnableLog
        >>> log_runnable = RunnableLog()
        >>> result = log_runnable.invoke("Hello, World!")
        >>> # This will log "Hello, World!" using logging.info
        >>> print(result)  # Output: "Hello, World!"
    """

    def __init__(
        self,
        output_func: Callable[[T], None] = logging.info,
        **kwargs,
    ):
        func = partial(
            self._identity_with_output,
            output_func=output_func
        )
        super().__init__(func, **kwargs)

    @staticmethod
    def _identity_with_output(
        x: T,
        output_func: Callable[[T,], None] | None = None,
    ) -> T:
        if output_func:
            output_func(x)
        return x
