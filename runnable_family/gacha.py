from langchain_core.runnables import (
    Runnable,
    RunnableLambda,
    RunnableParallel,
)
from langchain_core.runnables.base import Input, Output
from typing import Any


class RunnableGacha(Runnable[Input, Output]):
    ''' A simple implementation of Gacha Chain

    Here is "Gacha" means to run the same runnable multiple times in parallel
    '''

    _chain: Runnable[Input, Output]

    def __init__(
        self,
        runnable: Runnable[Input, Output],
        n: int = 10,
    ):
        self._chain = (
            RunnableParallel(**{str(i): runnable for i in range(n)})  # type: ignore  # noqa
            | RunnableLambda(lambda dic: dic.values())
            | RunnableLambda(list)
        ).with_types(
            input_type=runnable.InputType,
            output_type=list[runnable.OutputType],  # type: ignore
        )

    def invoke(self, *args, **kwargs) -> Output:
        return self._chain.invoke(*args, **kwargs)

    def __getattribute__(self, name: str) -> Any:
        if name in ["_chain", "invoke"]:
            return super().__getattribute__(name)
        try:
            return getattr(self._chain, name)
        except AttributeError:
            return super().__getattribute__(name)

    @property
    def InputType(self) -> type[Input]:
        return self._chain.InputType

    @property
    def OutputType(self) -> type[Output]:
        return self._chain.OutputType
