from langgraph.runtime import Runtime
from langchain_core.messages import SystemMessage

from workflows.states import AgenticRAGState, AgenticRAGContextSchema

def return_docs(state: AgenticRAGState, runtime : Runtime[AgenticRAGContextSchema]):
    """Return the documents."""
    docs = state["vector_docs"] + state["full_text_docs"]
    docs_string = "\n".join(f"Source : {doc.metadata['filename']}\n{doc.page_content}" for doc in docs)
    return {"messages": [SystemMessage(content=docs_string)]}