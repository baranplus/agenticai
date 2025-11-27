from .state import AgenticRAGState

def return_docs(state: AgenticRAGState):
    """Return the documents."""

    docs = state["docs"][0] + state["docs"][1]
    results = "\n".join(f"Source : {doc.metadata['source']}\n{doc.page_content}" for doc in docs)
    return {"messages": [{"role": "user", "content": results}]}