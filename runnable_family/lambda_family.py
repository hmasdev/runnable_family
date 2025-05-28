from functools import partial
from typing import Callable
from langchain_core.runnables import RunnableLambda
from langchain_core.runnables.base import Input, Output


class RunnablePartialLambda(RunnableLambda[Input, Output]):
    '''Runnable that binds keyword arguments to a function.

    Args:
        func: The function to bind the keyword arguments to.
        **kwargs: Keyword arguments to bind to the function.

    Example:
        >>> from runnable_family.lambda_family import RunnablePartialLambda
        >>> def my_func(x, a, b):
        ...     return x + a + b
        >>> partial_lambda = RunnablePartialLambda(my_func, a='A', b='B')
        >>> result = partial_lambda.invoke('x')
        >>> print(result)  # Output: 'xAB'
        xAB

    Note:
        This class is equivalent to `RunnableLambda(partial(func, **kwargs))`.
    '''

    def __init__(self, func: Callable[[Input], Output], **kwargs):
        super().__init__(partial(func, **kwargs))
