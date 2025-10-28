from .state import AgenticRAGState

def return_docs(state: AgenticRAGState):
    """Return the documents."""

    docs = state["docs"]
    results = "\n".join(doc.page_content for doc in docs)
    return {"messages": [{"role": "user", "content": results}]}