import langchain
from langchain_core.runnables import (
    Runnable,
    RunnableBranch,
    RunnableConfig,
    RunnableLambda,
    RunnablePassthrough,
    RunnableParallel,
)
from langchain_core.runnables.base import Input, Output
import langchain_core.runnables.graph
from langgraph.graph.graph import Graph, CompiledGraph, END
from typing import Callable
from uuid import uuid4
from .operator import RunnableAddConstant
from .standard import RunnableConstant

if langchain.__version__ < '0.3.0':
    from langchain.pydantic_v1 import create_model
else:
    from pydantic import create_model  # type: ignore


class RunnableLoopback(Runnable[Input, Output]):
    """Runnable that loops back the output to the input until a condition is met.
    This runnable is useful for scenarios where you want to repeatedly process
    the output of a runnable until a certain condition is satisfied, such as
    in iterative algorithms or feedback loops.

    Args:
        runnable (Runnable[Input, Output]): The runnable to be looped back.
            This is the main processing unit that will be executed repeatedly.
        condition (Runnable[Output, bool] | Callable[[Output], bool]): A
            condition that determines whether to continue looping back or not.
            If a callable is provided, it will be wrapped in a RunnableLambda.
        loopback (Runnable[Output, Input]): A runnable that takes the output
            of the main runnable and transforms it back into the input format
            for the next iteration.

    Attributes:
        _graph (CompiledGraph): Compiled graph of the runnable.
        _runnable (Runnable[Input, Output]): The main runnable to be looped back.
        _condition (Runnable[Output, bool]): Condition to determine if looping continues.
        _loopback (Runnable[Output, Input]): Runnable to transform output back to input.

    Example:
        >>> from runnable_family.loopback import RunnableLoopback
        >>> from langchain_core.runnables import RunnableLambda
        >>> def my_runnable(x):
        ...     return x + 1
        >>> def my_condition(output):
        ...     return output < 5
        >>> def my_loopback(output):
        ...     return output * 2
        >>> loopback_runnable = RunnableLoopback(
        ...    runnable=RunnableLambda(my_runnable),
        ...    condition=RunnableLambda(my_condition),
        ...    loopback=RunnableLambda(my_loopback)
        ... )
        >>> result = loopback_runnable.invoke(0)
        >>> print(result)  # Output: 7
        7
        >>> # 0 -(my_runnable)-> 1 -(my_loopback)-> 2 -(my_runnable)-> 3 -(my_loopback)-> 6 -(my_runnable)-> 7
    """  # noqa

    _graph: CompiledGraph
    '''Compiled graph of the runnable.'''

    _runnable: Runnable[Input, Output]
    '''Runnable to be looped back.'''
    _condition: Runnable[Output, bool]
    '''Condition to looping back.'''
    _loopback: Runnable[Output, Input]
    '''Runnable to loop back the output to the input.'''

    def __init__(
        self,
        runnable: Runnable[Input, Output],
        condition: Runnable[Output, bool] | Callable[[Output], bool],
        loopback: Runnable[Output, Input],
    ):
        # components
        self._runnable = runnable
        if not isinstance(condition, Runnable):
            self._condition = RunnableLambda(condition)
        else:
            self._condition = condition
        self._loopback = loopback

        # create graph
        graph = Graph()
        graph.add_node('runnable', runnable)
        graph.add_node('loopback', loopback)
        graph.add_conditional_edges(
            'runnable',
            condition | RunnableLambda(lambda b: 'continue' if b else 'end'),
            {
                'continue': 'loopback',
                'end': END,
            },
        )
        graph.add_edge('loopback', 'runnable')
        graph.set_entry_point('runnable')
        self._graph = graph.compile()

    def invoke(self, input: Input, *args, **kwargs) -> Output:
        return self._graph.invoke(input, *args, **kwargs)  # type: ignore

    @classmethod
    def with_n_loop(
        cls: type[Runnable[Input, Output]],
        n: int,
        runnable: Runnable[Input, Output],
        loopback: Runnable[Output, Input],
        output_key_header: str = "output",
        counter_key_header: str = "counter",
    ) -> Runnable[Input, Output]:
        '''Returns a new RunnableLoopback with n loops.
        '''
        if n == 0:
            return RunnablePassthrough()  # type: ignore
        if n == 1:
            return runnable

        _id: str = str(uuid4())
        output_key: str = f"{output_key_header}_{_id}"
        counter_key: str = f"{counter_key_header}_{_id}"
        already_initilized: RunnableLambda[dict | Input, bool] = (
            RunnableLambda(lambda x: (
                isinstance(x, dict)
                and (output_key in x)
                and (counter_key in x)
            ))
        )
        _runnable: RunnableBranch[dict | Input, dict] = RunnableBranch(
            (
                already_initilized,
                {
                    output_key: RunnablePassthrough().pick(output_key) | runnable,  # noqa
                    counter_key: RunnablePassthrough().pick(counter_key),
                }
            ),
            {
                # initialize
                output_key: runnable,
                counter_key: RunnableConstant(1),
            }
        )
        _condition = RunnablePassthrough().pick(counter_key) | RunnableLambda(lambda x: x < n)  # noqa
        _loopback = RunnableParallel(**{
            output_key: RunnablePassthrough().pick(output_key) | loopback,
            counter_key: RunnablePassthrough().pick(counter_key) | RunnableAddConstant(1),  # noqa
        })  # type: ignore
        return cls(
            runnable=_runnable,  # type: ignore
            condition=_condition,  # type: ignore
            loopback=_loopback,  # type: ignore
        ) | RunnablePassthrough().pick(output_key)

    def get_graph(self, config: RunnableConfig | None = None) -> langchain_core.runnables.graph.Graph:  # noqa
        graph = langchain_core.runnables.graph.Graph()
        # create input/oupput nodes
        try:
            input_node = graph.add_node(self.get_input_schema(config))
        except TypeError:
            input_node = graph.add_node(create_model(self.get_name("Input")))  # type: ignore # noqa
        try:
            output_node = graph.add_node(self.get_output_schema(config))
        except TypeError:
            output_node = graph.add_node(create_model(self.get_name("Output")))  # type: ignore # noqa
        # cretae sugraphs
        runnable_graph = self._runnable.get_graph(config)
        condition_graph = self._condition.get_graph(config)
        loopback_graph = self._loopback.get_graph(config)
        graph.extend(runnable_graph)
        graph.extend(condition_graph)
        graph.extend(loopback_graph)
        # connect nodes
        # connect input/output nodes to subgraphs
        graph.add_edge(input_node, runnable_graph.first_node())  # type: ignore
        graph.add_edge(condition_graph.last_node(), output_node)  # type: ignore  # noqa
        # connect subgraphs
        graph.add_edge(runnable_graph.last_node(), condition_graph.first_node())    # type: ignore # noqa
        graph.add_edge(condition_graph.last_node(), loopback_graph.first_node())    # type: ignore # noqa
        graph.add_edge(runnable_graph.first_node(), loopback_graph.last_node())  # type: ignore  # noqa
        # NOTE: the edge from loopback_graph to runnable_graph is inverted
        #       graph.add_edge(loopback_graph.last_node(), runnable_graph.first_node())  # noqa

        return graph

    @property
    def InputType(self) -> type[Input]:
        return self._runnable.InputType

    @property
    def OutputType(self) -> type[Output]:
        return self._runnable.OutputType
