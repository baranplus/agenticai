from langgraph.graph.state import CompiledStateGraph

from workflows.graph import WorkflowGraphBuilder
from workflows.configs.agentic_rag import AGENTIC_RAG_WORKFLOW
from .states import (
    AgenticRAGState,
    AgenticRAGContextSchema,
    SmartSQLPipelineState,
    SmartSQLPipelineContextSchema
)

agentic_rag_graph = WorkflowGraphBuilder(
    state_schema=AgenticRAGState, 
    context_schema=AgenticRAGContextSchema,
    workflow_config=AGENTIC_RAG_WORKFLOW
).build()

def get_agentic_rag_graph() -> CompiledStateGraph:
    """Dependency provider for FastAPI."""
    return agentic_rag_graph





