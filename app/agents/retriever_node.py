import os
from langchain.schema import Document
from weaviate.collections.classes.internal import Object as WeaviateObject
from weaviate.classes.query import BM25Operator
from typing import List

from .state import State
from db import weaviate_client
from db.vector_store import get_weaviate_vector_store
from llm import embedding_func

HYBRID_SEARCH_ALPHA = float(os.environ.get("HYBRID_SEARCH_ALPHA"))

def convert_weaviate_objects_to_langchain_docs(weaviate_objects: List[WeaviateObject]) -> List[Document]:
    """
    Converts a list of Weaviate Object instances into a list of LangChain Document objects.
    """
    langchain_docs = []

    for obj in weaviate_objects:

        page_content = obj.properties.get("content", "")

        metadata = {}

        for key, value in obj.properties.items():
            if key != "content":
                metadata[key] = value

        metadata["weaviate_uuid"] = str(obj.uuid)

        if obj.metadata and obj.metadata.distance is not None:
            metadata["distance"] = obj.metadata.distance
        if obj.metadata and obj.metadata.score is not None:
            metadata["score"] = obj.metadata.score

        doc = Document(
            page_content=page_content,
            metadata=metadata
        )
        langchain_docs.append(doc)

    return langchain_docs

def retrieve_documents(state : State) -> str:

    """Query vector database. Use this for any question regarding national rules of IR"""

    weaviate_vector_store = get_weaviate_vector_store(weaviate_client, state["collection_name"], embedding_func.embeddings_model)
    retriever = weaviate_vector_store.as_retriever(search_kwargs={"k" : state["top_k"]})
    query = state["messages"][-1].content
    docs = retriever.invoke(query)
    results = "\n".join(doc.page_content for doc in docs)

    return {"messages": [{"role" : "user", "content" : results}], "rewrite_count" : state["rewrite_count"], "docs" : docs, "sourcing" : state["sourcing"]}

def retrieve_documents_use_weaviate_embedding(state : State) -> str:

    """Query vector database. Use this for any question regarding national rules of IR"""

    collection = weaviate_client.collections.get(state["collection_name"])
    query = state["messages"][-1].content

    response = collection.query.hybrid(
        query=query, 
        limit=state["top_k"], 
        alpha=HYBRID_SEARCH_ALPHA, 
        bm25_operator=BM25Operator.or_(minimum_match=2)
    )
    docs = convert_weaviate_objects_to_langchain_docs(response.objects)
    results = "\n".join(doc.page_content for doc in docs)

    return {"messages": [{"role" : "user", "content" : results}], "rewrite_count" : state["rewrite_count"], "docs" : docs, "sourcing" : state["sourcing"]}