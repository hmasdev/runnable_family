from functools import partial
import logging
from typing import Callable, TypeVar
from langchain_core.runnables import RunnableLambda

T = TypeVar("T")


class RunnableLog(RunnableLambda[T, T]):
    '''Runnable that logs the input before returning it.

    Args:
        output_func: Function to call with the input.
            Default is logging.info.
    '''

    def __init__(
        self,
        output_func: Callable[[T], None] = logging.info,
        **kwargs,
    ):
        func = partial(
            self.__identity_with_output,
            output_func=output_func
        )
        super().__init__(func, **kwargs)

    @staticmethod
    def __identity_with_output(
        x: T,
        output_func: Callable[[T,], None] | None = None,
    ) -> T:
        if output_func:
            output_func(x)
        return x
