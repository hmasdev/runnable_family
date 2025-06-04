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
        super().__init__(self._return_constant, *args, **kwargs)
        self._constant = constant

    def _return_constant(self, _: Input) -> Output:
        """Return the constant value."""
        return self._constant
