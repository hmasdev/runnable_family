from functools import partial
from typing import Callable
from langchain_core.runnables import RunnableLambda
from langchain_core.runnables.base import Input, Output


class RunnablePartialLambda(RunnableLambda[Input, Output]):
    '''RunnableLambda with keyword arguments bound.

    Args:
        func: Either sync or async callable
        **kwargs: Keyword arguments to bound to the function.
    '''

    def __init__(self, func: Callable[[Input], Output], **kwargs):
        super().__init__(partial(func, **kwargs))
