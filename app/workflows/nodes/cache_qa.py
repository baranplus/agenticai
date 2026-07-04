from langchain_core.messages import AIMessage, HumanMessage
from langgraph.runtime import Runtime

from workflows.states import AgenticRAGState, AgenticRAGContextSchema


def cache_last_question_answer(
    state: AgenticRAGState,
    runtime: Runtime[AgenticRAGContextSchema],
):
    """Cache the latest user question and generated answer in Redis."""
    question = None
    answer = None

    if not question and state["messages"]:
        question = getattr(state["messages"][0], "content", None)

    if not answer and state["messages"]:
        answer = getattr(state["messages"][-1], "content", None)

    if question and answer:
        runtime.context.redis_manager.cache_qa_pair(
            question=question,
            answer=answer,
            metadata={"source": "agentic_rag_workflow"},
            ttl=86400,
        )

    return state
