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




# class WorkflowGraphBuilder:
#     """
#     A class responsible for building and compiling an Agentic RAG workflow graph
#     using LangGraph's StateGraph.

#     This encapsulates the graph construction logic, making it configurable,
#     reusable, and easier to test or extend.
#     """

#     def __init__(
#         self,
#         state_schema: type ,
#         context_schema : type
#     ):
#         """
#         Initialize the graph builder.

#         Args:
#             state_schema: The state class/annotation used in the graph (e.g., AgenticRAGState).
#                           Defaults to AgenticRAGState if not provided.
#             context_schema: The context that provides callable instances
#         """
#         self.state_schema = state_schema
#         self.context_schema = context_schema

#         self.nodes = {
#             "extract_keywords": extract_keywords_initial,
#             "retrieve_documents_by_vector_search" : retrieve_documents_by_vector_search,
#             "retrieve_documents_by_fulltext_search" : retrieve_documents_by_fulltext_search,
#             "merge_after_retrieve" : merge_after_retrieve,
#             "return_docs" : return_docs,
#             "generate_answer_branching" : generate_answer_branching,
#             "generate_answer_agentic_rag_for_vector_search" : generate_answer_agentic_rag_for_vector_search,
#             "generate_answer_agentic_rag_for_fulltext_search" : generate_answer_agentic_rag_for_fulltext_search,
#             "show_source" : show_source
#         }

#     def build_graph(self) -> CompiledStateGraph:
#         """Construct and return the compiled LangGraph workflow."""

#         graph_builder = StateGraph(self.state_schema, context_schema=self.context_schema)

#         for node_name, node_func in self.nodes.items():
#             graph_builder.add_node(node_name, node_func)

#         graph_builder.add_edge(START, "extract_keywords")

#         graph_builder.add_edge("extract_keywords", "retrieve_documents_by_vector_search")
#         graph_builder.add_edge("extract_keywords", "retrieve_documents_by_fulltext_search")

#         graph_builder.add_edge("retrieve_documents_by_vector_search", "merge_after_retrieve")
#         graph_builder.add_edge("retrieve_documents_by_fulltext_search", "merge_after_retrieve")

#         graph_builder.add_conditional_edges(
#             "merge_after_retrieve",
#             return_docs_or_generate_answer,
#             {
#                 "return_docs" : "return_docs",
#                 "generate_answer" : "generate_answer_branching"
#             }
#         )

#         graph_builder.add_edge("return_docs", END)

#         graph_builder.add_edge("generate_answer_branching", "generate_answer_agentic_rag_for_vector_search")
#         graph_builder.add_edge("generate_answer_branching", "generate_answer_agentic_rag_for_fulltext_search")

#         graph_builder.add_edge("generate_answer_agentic_rag_for_vector_search", "show_source")
#         graph_builder.add_edge("generate_answer_agentic_rag_for_fulltext_search", "show_source")

#         graph_builder.add_edge("show_source", END)

#         graph = graph_builder.compile()

#         return graph

#     def __call__(self) -> CompiledStateGraph:
#         """
#         Make the instance callable for convenience:
#         builder = AgenticRAGGraphBuilder()
#         graph = builder()
#         """
#         return self.build_graph()


# def build_graph_smart_sql():

#     graph_builder = StateGraph(SmartSQLPipelineState)

#     graph_builder.add_node(execute_sql)
#     graph_builder.add_node(generate_answer_smart_sql)

#     graph_builder.add_edge(START, "execute_sql")
#     graph_builder.add_edge("execute_sql", "generate_answer_smart_sql")
#     graph_builder.add_edge("generate_answer_smart_sql", END)
#     graph = graph_builder.compile()

#     return graph
    