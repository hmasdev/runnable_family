from langchain_core.runnables import (
    Runnable,
    RunnableAssign,
    RunnableParallel,
    RunnablePassthrough,
    RunnableSequence,
)
from langchain_core.runnables.base import Input, Output
from typing import TypeVar

InterMediate = TypeVar("InterMediate", covariant=True)
InterMediate2 = TypeVar("InterMediate2", covariant=True)


class RunnableSelfRefine(RunnableSequence[Input, Output]):
    """A Runnable that implements the Self-Refine methodology for iterative
    refinement using LangChain Runnables. It allows for a sequence of
    refinement steps where the output of one step can be used as feedback
    for the next step.

    This runnable is inspired by the self-refine approach in
    "Self-Refine: Iterative Refinement with Self-Feedback"
    (https://arxiv.org/pdf/2303.17651.pdf).

    Args:
        runnable: The initial runnable that produces an intermediate output.
        feedback: A runnable that takes the intermediate output and produces
            feedback for refinement.
        refine: A runnable that takes the input, intermediate output, and
            feedback to produce the final output.
        input_key: The key in the input dictionary for the initial input.
        output_key: The key in the output dictionary for the final output.
        feedback_key: The key in the input dictionary for the feedback.

    Example:
        >>> from langchain_core.runnables import RunnableLambda
        >>> from runnable_family.self_refine import RunnableSelfRefine
        >>> def initial_runnable(input):
        ...     return input + " initial"
        >>> def feedback_runnable(data):
        ...     return f"feedback: {data['input']} -> {data['output']}"
        >>> def refine_runnable(data):
        ...     return f"refined: '{data['input']}' '{data['output']}' with FB '{data['feedback']}'"
        >>> self_refine_runnable = RunnableSelfRefine(
        ...     runnable=RunnableLambda(initial_runnable),
        ...     feedback=RunnableLambda(feedback_runnable),
        ...     refine=RunnableLambda(refine_runnable),
        ...     input_key="input",
        ...     output_key="output",
        ...     feedback_key="feedback",
        ... )
        >>> result = self_refine_runnable.invoke("test")
        >>> print(result)
        refined: 'test' 'test initial' with FB 'feedback: test -> test initial'
    """  # noqa

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
        super().__init__(
            RunnableParallel(**{
                input_key: RunnablePassthrough(),  # type: ignore
                output_key: runnable,
            }),
            RunnableAssign({
                feedback_key: feedback,  # type: ignore
            }),
            refine,
        )
