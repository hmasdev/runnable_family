from langchain_core.runnables import (
    Runnable,
    RunnableBranch,
    RunnableConfig,
    RunnableLambda,
    RunnablePassthrough,
    RunnableParallel,
)
from langchain_core.runnables.base import Input, Output
from langchain_core.runnables.graph import Graph
from typing import Callable
from uuid import uuid4
from .basic import RunnableConstant, RunnableAdd


class RunnableLoopback(Runnable[Input, Output]):
    '''Runnable that loops back the output to the input.
    '''

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
        self._runnable = runnable
        if not isinstance(condition, Runnable):
            self._condition = RunnableLambda(condition)
        else:
            self._condition = condition
        self._loopback = loopback

    def invoke(self, input: Input, *args, **kwargs) -> Output:
        return (
            self._runnable
            | RunnableBranch(
                (self._condition, self._loopback | self),
                RunnablePassthrough(),
            )
        ).invoke(input, *args, **kwargs)

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
            counter_key: RunnablePassthrough().pick(counter_key) | RunnableAdd(1),  # noqa
        })
        return cls(
            runnable=_runnable,  # type: ignore
            condition=_condition,  # type: ignore
            loopback=_loopback,  # type: ignore
        ) | RunnablePassthrough().pick(output_key)

    def get_graph(self, config: RunnableConfig | None = None) -> Graph:

        graph = Graph()
        # create input/oupput nodes
        input_node = graph.add_node(self.get_input_schema(config))
        output_node = graph.add_node(self.get_output_schema(config))
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
