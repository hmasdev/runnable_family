from langchain_core.runnables import RunnableLambda
from langchain_core.runnables.base import Input, Output


class RunnableConstant(RunnableLambda[Input, Output]):
    '''Runnable that always returns a constant output.
    '''

    def __init__(self, constant: Output, *args, **kwargs):
        super().__init__(lambda _: constant, *args, **kwargs)


class RunnableAdd(RunnableLambda[Input, Output]):
    '''Runnable that adds a constant to the input.

    Args:
        constant: Constant to be added.
        left: If True, the constant is added to the left side.
            Otherwise, it is added to the right side.
            That is, x + constant if left is True, and constant + x otherwise.
    '''
    _constant: Input
    _left: bool

    def __init__(
        self,
        constant: Input,
        left: bool = True,
        *args,
        **kwargs,
    ):
        self._constant = constant
        self._left = left
        super().__init__(self._add, *args, **kwargs)

    def _add(self, x: Input) -> Output:
        if not hasattr(x, "__add__"):
            raise TypeError(f"Cannot add {x} and {self._constant}")
        if self._left:
            return x + self._constant  # type: ignore
        else:
            return self._constant + x  # type: ignore
