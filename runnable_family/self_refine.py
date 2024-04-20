from langchain_core.runnables import (
    Runnable,
    RunnableParallel,
    RunnablePassthrough,
)
from langchain_core.runnables.base import Input, Output
from typing import Any, TypeVar

InterMediate = TypeVar("InterMediate", covariant=True)
InterMediate2 = TypeVar("InterMediate2", covariant=True)


class RunnableSelfRefine(Runnable[Input, Output]):
    ''' A simple implementation of Self-Refine Chain as described in the paper:

    Ref. https://arxiv.org/pdf/2303.17651.pdf
    '''

    _self_refine_chain: Runnable[Input, Output]

    def __init__(
        self,
        runnable: Runnable[Input, InterMediate],
        feedback: Runnable[dict[str, InterMediate], InterMediate2],
        refine: Runnable[dict[str, Input | InterMediate | InterMediate2], Output],  # noqa
        input_key: str = "input",
        output_key: str = "output",
        feedback_key: str = "feedback",
    ):
        self._self_refine_chain = (
            RunnableParallel(**{
                input_key: RunnablePassthrough(),  # type: ignore
                output_key: runnable,
            })
            | RunnableParallel(**{
                input_key: RunnablePassthrough().pick(input_key),
                output_key: RunnablePassthrough().pick(output_key),
                feedback_key: feedback,
            })  # type: ignore
            | refine
        ).with_types(
            input_type=runnable.InputType,  # type: ignore
            output_type=refine.OutputType,
        )

    def invoke(self, *args, **kwargs) -> Output:
        # To make it a concrete class
        return self._self_refine_chain.invoke(*args, **kwargs)

    def __getattribute__(self, name: str) -> Any:
        if name in ["_self_refine_chain", "invoke"]:
            return super().__getattribute__(name)
        try:
            return getattr(self._self_refine_chain, name)
        except AttributeError:
            return super().__getattribute__(name)

    @property
    def InputType(self) -> type[Input]:
        return self._self_refine_chain.InputType

    @property
    def OutputType(self) -> type[Output]:
        return self._self_refine_chain.OutputType
