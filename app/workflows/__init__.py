from langgraph.graph.state import CompiledStateGraph

from .graph import WorkflowGraphBuilder
from configs.env_configs import env_config

from .states import (
    AgenticRAGState,
    AgenticRAGContextSchema,
    SmartSQLPipelineState,
    SmartSQLPipelineContextSchema
)

agentic_rag_graph = WorkflowGraphBuilder(AgenticRAGState, AgenticRAGContextSchema).build_graph()

def get_agentic_rag_graph() -> CompiledStateGraph:
    """Dependency provider for FastAPI."""
    return agentic_rag_graph





