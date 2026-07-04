from langgraph.runtime import Runtime
from typing import Literal

from workflows.states import AgenticRAGState, AgenticRAGContextSchema


def return_docs_or_generate_answer(
    state : AgenticRAGState, 
    runtime : Runtime[AgenticRAGContextSchema]
) -> Literal["return_docs", "generate_answer"]:
    
    if state["return_docs"]:
        return "return_docs"
    return "generate_answer"


def continue_after_cache_retrieval(
    state: AgenticRAGState,
    runtime: Runtime[AgenticRAGContextSchema],
) -> Literal["end", "continue"]:
    if state.get("cache_question_retrieval_successful", False):
        return "end"
    return "continue"



