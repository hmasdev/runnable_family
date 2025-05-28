from langchain_core.runnables import RunnableLambda
from langchain_core.runnables.base import Input, Output


class RunnableConstant(RunnableLambda[Input, Output]):
    """Runnable that always returns a constant value.

    Args:
        constant: The constant value to return, regardless of the input.
            The input is ignored.

    Attributes:
        _constant (Output): The constant value to return.

    Example:
        >>> from runnable_family.basic import RunnableConstant
        >>> constant_runnable = RunnableConstant("Hello, World!")
        >>> result = constant_runnable.invoke("Any input")
        >>> print(result)  # Output: "Hello, World!"
        Hello, World!
    """

    _constant: Output

    def __init__(self, constant: Output, *args, **kwargs):
        super().__init__(lambda _: constant, *args, **kwargs)


class RunnableAdd(RunnableLambda[Input, Output]):
    """Runnable that adds a constant to the input.

    Args:
        constant: The constant value to add to the input.
            The input type must support addition operation.
        prepend: If True, adds the constant to the left side of the input.
            If False, adds the constant to the right side of the input.
            That is, `constant + input` if `prepend=True` and
            `input + constant` if `prepend=False`.

    Attributes:
        _constant (Input): The constant value to add.
        _prepend (bool): Whether to prepend the constant to the input.

    Example:
        >>> from runnable_family.basic import RunnableAdd
        >>> add_runnable = RunnableAdd(1)
        >>> result = add_runnable.invoke(10)
        >>> print(result)  # Output: 11
        11
        >>> add_runnable = RunnableAdd([1], prepend=False)
        >>> result = add_runnable.invoke([10])
        >>> print(result)  # Output: [10, 1]
        [10, 1]
        >>> add_runnable_right = RunnableAdd([1], prepend=True)
        >>> result = add_runnable_right.invoke([10])
        >>> print(result)  # Output: [1, 10]  # type: ignore
        [1, 10]
    """
    _constant: Input
    _prepend: bool

    def __init__(
        self,
        constant: Input,
        prepend: bool = False,
        *args,
        **kwargs,
    ):
        self._constant = constant
        self._prepend = prepend
        super().__init__(self._add, *args, **kwargs)

    def _add(self, x: Input) -> Output:
        if not hasattr(x, "__add__"):
            raise TypeError(f"Cannot add {x} and {self._constant}")
        if self._prepend:
            return self._constant + x  # type: ignore
        else:
            return x + self._constant  # type: ignore
