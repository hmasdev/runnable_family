from functools import partial, wraps
from typing import Callable, Iterable
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


class RunnableUnpackLambda(RunnableLambda[Iterable[Input], Output]):
    '''
    Runnable that unpacks an iterable of inputs into the function arguments.
    This allows the function to accept multiple inputs as if they were separate
    arguments.

    Args:
        func: The function to unpack the iterable inputs into.

    Example:
        >>> from runnable_family.lambda_family import RunnableUnpackLambda
        >>> def my_func(x, y, z):
        ...     return (x + y, z)
        >>> unpack_lambda = RunnableUnpackLambda(my_func)
        >>> result = unpack_lambda.invoke([1, 2, 3])
        >>> print(result)  # Output: (3, 3)
        (3, 3)

    Note:
        This class is equivalent to `RunnableLambda(lambda inputs: func(*inputs))`.
        It allows you to pass a list or tuple of inputs directly to the function.
    '''  # noqa

    def __init__(
        self,
        func: Callable[..., Output],
    ):
        super().__init__(self._unpack_deco(func))

    @staticmethod
    def _unpack_deco(
        func: Callable[..., Output],
    ) -> Callable[[Iterable[Input]], Output]:
        '''
        Decorator to unpack an iterable of inputs into the function arguments.
        This allows the function to accept multiple inputs as if they were
        separate arguments.
        '''  # noqa
        @wraps(func)
        def unpacked_func(inputs: Iterable[Input]) -> Output:
            return func(*inputs)
        return unpacked_func


class RunnableDictUnpackLambda(RunnableLambda[dict[str, Input], Output]):
    '''
    Runnable that unpacks a dictionary of inputs into the function arguments.
    This allows the function to accept multiple inputs as if they were separate
    arguments.

    Args:
        func: The function to unpack the dictionary inputs into.

    Example:
        >>> from runnable_family.lambda_family import RunnableDictUnpackLambda
        >>> def my_func(x, y, z):
        ...     return (x + y, z)
        >>> unpack_lambda = RunnableDictUnpackLambda(my_func)
        >>> result = unpack_lambda.invoke({'x': 1, 'y': 2, 'z': 3})
        >>> print(result)  # Output: (3, 3)
        (3, 3)

    Note:
        This class is equivalent to `RunnableLambda(lambda inputs: func(**inputs))`.
        It allows you to pass a dictionary of inputs directly to the function.
    '''  # noqa

    def __init__(
        self,
        func: Callable[..., Output],
    ):
        super().__init__(self._unpack_dict_deco(func))

    @staticmethod
    def _unpack_dict_deco(
        func: Callable[..., Output],
    ) -> Callable[[dict[str, Input]], Output]:
        '''
        Decorator to unpack a dictionary of inputs into the function arguments.
        This allows the function to accept multiple inputs as if they were
        separate arguments.
        '''  # noqa
        @wraps(func)
        def unpacked_func(inputs: dict[str, Input]) -> Output:
            return func(**inputs)
        return unpacked_func
