import os
import itertools
import random
from collections import Counter
from langchain.schema import Document
from weaviate.collections.classes.internal import Object as WeaviateObject
from weaviate.classes.query import BM25Operator
from typing import List, Iterable, Any

from .state import AgenticRAGState
from db import weaviate_client
from db.vector_store import get_weaviate_vector_store
from llm import embedding_func
from utils.logger import logger

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

def get_top_sources(documents, top_n_source=10, top_n_uuids = 10) -> List[Document]:

    """
    Return documents that:
    - Belong to one of the top N most frequent sources
    - Have one of the top N most frequent weaviate_uuids
    - Have globally unique weaviate_uuids (no duplicates)
    """

    if not documents:
        return []

    source_to_docs = {}
    uuid_to_doc = {}
    uuid_counter = Counter()
    source_counter = Counter()

    for doc in documents:
        source = doc.metadata.get('source')
        uuid = doc.metadata.get('weaviate_uuid')

        if source:
            source_counter[source] += 1
            source_to_docs.setdefault(source, []).append(doc)

        if uuid:
            uuid_counter[uuid] += 1
            
            uuid_to_doc.setdefault(uuid, doc)

    top_sources = {src for src, _ in source_counter.most_common(top_n_source)}
    top_uuids = {uuid for uuid, _ in uuid_counter.most_common(top_n_uuids)}

    final_docs = []
    seen_uuids = set()

    for uuid in top_uuids:
        if uuid in uuid_to_doc:
            doc = uuid_to_doc[uuid]
            source = doc.metadata.get('source')
            if source in top_sources and uuid not in seen_uuids:
                final_docs.append(doc)
                seen_uuids.add(uuid)

    return final_docs

def sample_combinations(keywords: List[str], max_samples: int = 10, seed: int | None = None,) -> Iterable[str]:
    """
    Yield a limited number of non-empty keyword combinations.
    - If total combinations ≤ max_samples → yield all of them.
    - Otherwise → yield a random sample of `max_samples`.
    """
    if not keywords:
        return

    all_combos = []
    for r in range(1, len(keywords) + 1):
        all_combos.extend(" ".join(combo) for combo in itertools.combinations(keywords, r))

    total = len(all_combos)
    if total == 0:
        return

    n_to_yield = min(total, max_samples)

    rng = random.Random(seed)
    chosen = rng.sample(all_combos, n_to_yield)

    for combo in chosen:
        yield combo

def retrieve_documents(state : AgenticRAGState) -> str:

    """Query vector database. Use this for any question regarding national rules of IR"""

    weaviate_vector_store = get_weaviate_vector_store(weaviate_client, state["collection_name"], embedding_func.embeddings_model)
    retriever = weaviate_vector_store.as_retriever(search_kwargs={"k" : state["top_k"]})
    query = state["messages"][-1].content
    docs = retriever.invoke(query)
    results = "\n".join(doc.page_content for doc in docs)

    return {"messages": [{"role" : "user", "content" : results}], "rewrite_count" : state["rewrite_count"], "docs" : docs, "sourcing" : state["sourcing"]}

def retrieve_documents_use_weaviate_embedding(state : AgenticRAGState) -> str:

    """Query vector database. Use this for any question regarding national rules of IR"""

    collection = weaviate_client.collections.get(state["collection_name"])
    query = state["messages"][-1].content
    initial_question = state["messages"][0].content

    keywords = query.split(",")

    for combo in sample_combinations(keywords=keywords, max_samples=1):
        keywords.append(combo)
    keywords.append(initial_question)
    logger.info(f"\n\nKeywords : {keywords}\n\n")
    aggregated_docs = []

    for keyword in keywords:

        response = collection.query.hybrid(
            query=keyword, 
            limit=state["top_k"], 
            alpha=HYBRID_SEARCH_ALPHA, 
            # bm25_operator=BM25Operator.or_(minimum_match=2)
        )

        docs = convert_weaviate_objects_to_langchain_docs(response.objects)
        aggregated_docs.extend(docs)

    final_docs = get_top_sources(aggregated_docs, top_n_source=state["top_k"], top_n_uuids=state["top_k"])

    results = "\n".join(doc.page_content for doc in final_docs)

    return {"messages": [{"role" : "user", "content" : results}], "docs" : final_docs}