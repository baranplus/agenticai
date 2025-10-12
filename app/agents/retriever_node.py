from .state import State
from db import weaviate_vector_store

def retrieve_documents(state : State) -> str:

    """Query vector database. Use this for any question regarding national rules of IR"""

    retriever = weaviate_vector_store.as_retriever(search_kwargs={"k" : 5})
    query = state["messages"][-1].content
    docs = retriever.invoke(query)
    results = "\n".join(doc.page_content for doc in docs)

    return {"messages": [{"role" : "user", "content" : results}], "rewrite_count" : state["rewrite_count"], "docs" : docs, "sourcing" : state["sourcing"]}