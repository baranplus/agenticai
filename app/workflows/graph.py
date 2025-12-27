from langgraph.graph import StateGraph
from langgraph.graph.state import CompiledStateGraph
from dataclasses import dataclass
from typing import Callable, Dict, List, Tuple

@dataclass(frozen=True)
class ConditionalEdgeConfig:
    source: str
    condition_fn: Callable
    mapping: Dict[str, str]

@dataclass(frozen=True)
class WorkflowConfig:
    nodes: Dict[str, Callable]
    edges: List[Tuple[str, str]]
    conditional_edges: List[ConditionalEdgeConfig]

class WorkflowGraphBuilder:
    """
    Generic LangGraph workflow builder.
    Fully driven by WorkflowConfig.
    """

    def __init__(
        self,
        *,
        state_schema: type,
        context_schema: type,
        workflow_config: WorkflowConfig,
    ):
        self.state_schema = state_schema
        self.context_schema = context_schema
        self.config = workflow_config

    def build(self) -> CompiledStateGraph:
        graph = StateGraph(
            self.state_schema,
            context_schema=self.context_schema,
        )

        for name, fn in self.config.nodes.items():
            graph.add_node(name, fn)

        for src, dst in self.config.edges:
            graph.add_edge(src, dst)

        for cond in self.config.conditional_edges:
            graph.add_conditional_edges(
                cond.source,
                cond.condition_fn,
                cond.mapping,
            )

        return graph.compile()

    def __call__(self) -> CompiledStateGraph:
        return self.build()
    