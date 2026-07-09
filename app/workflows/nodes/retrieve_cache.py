from langchain_core.messages import AIMessage
from langgraph.runtime import Runtime

from workflows.states import AgenticRAGState, AgenticRAGContextSchema
from utils.logger import logger

def retrieve_cached_question_answer(
    state: AgenticRAGState,
    runtime: Runtime[AgenticRAGContextSchema],
):
    """Check Redis for a cached answer for the latest user question."""
    question = None
    if state.get("messages"):
        question = getattr(state["messages"][0], "content", None)

    if not question:
        return {"cache_question_retrieval_successful": False}

    # Get mongodb_name from runtime context
    mongodb_name = state["mongodb_dbname"]
    
    cached_answer = runtime.context.redis_manager.get_answer_by_question(question, mongodb_name)

    if cached_answer and cached_answer.get("answer"):
        logger.info(f"Found cached answer for question: {question}")
        answer_message = AIMessage(
            content=cached_answer["answer"],
            additional_kwargs={"source": "cache"},
        )
        return {
            "messages": [answer_message],
            "cache_question_retrieval_successful": True,
        }

    return {"cache_question_retrieval_successful": False}
