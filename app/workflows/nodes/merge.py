from langgraph.runtime import Runtime
from workflows.states import AgenticRAGState, AgenticRAGContextSchema

def merge_after_retrieve(state : AgenticRAGState, runtime : Runtime[AgenticRAGContextSchema]):
    """
        merging path after retrieving docs from vector search and full-text search
    """
    return state