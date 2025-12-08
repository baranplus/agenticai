import os
import itertools
import random
from collections import Counter
from langchain.schema import Document
from weaviate.collections.classes.internal import Object as WeaviateObject
from weaviate.classes.query import Filter
from typing import List, Iterable, Dict, Any

from .state import AgenticRAGState
from db import weaviate_client, mongodb_manager
from utils.logger import logger

HYBRID_SEARCH_ALPHA = float(os.environ.get("HYBRID_SEARCH_ALPHA"))

def convert_mongodb_raw_docs_to_langchain_document(raw_docs : List[Dict[str, Any]])-> List[Document]:
    """
    Converts a list of MongoDB Raw Dics instances into a list of LangChain Document objects.
    """
    langchain_docs = []

    for obj in raw_docs:

        page_content = obj.get("content", "")

        metadata = {}

        for key, value in obj.items():
            if key != "content":
                if key == "filename":
                    metadata["source"] = value
                else:
                    metadata[key] = value

        metadata["uuid"] = str(obj.get("_id"))

        doc = Document(
            page_content=page_content,
            metadata=metadata
        )
        langchain_docs.append(doc)

    return langchain_docs

def convert_mongodb_raw_docs_to_langchain_document_new(raw_docs: List[Dict[str, Any]]):
    langchain_docs = []

    for obj in raw_docs:

        page_content = obj.get("content", "")
        metadata = {}

        for key, value in obj.items():
            if key != "content":
                if key == "filename":  # NEW name
                    metadata["source"] = value
                else:
                    metadata[key] = value

        metadata["uuid"] = str(obj.get("_id"))

        doc = Document(page_content=page_content, metadata=metadata)
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

def sort_documents_by_score(docs : List[Document], top_k : int = 50) -> List[Document]:
    return sorted(docs, key=lambda d: d.metadata.get("score", 0), reverse=True)[:top_k]

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

    source_name = None

    query = state["messages"][-1].content
    initial_question = state["messages"][0].content

    keywords = query.split(",")

    for combo in sample_combinations(keywords=keywords, max_samples=1):
        keywords.append(combo)
    
    keywords.append(initial_question)

    logger.info(f"\n\nKeywords : {keywords}\n\n")

    aggregated_docs_vector = []
    aggregated_docs_text = []

    for keyword in keywords:

        mongo_docs_raw = mongodb_manager.full_text_search_new(state["mongodb_db"], state["mongodb_text_collection"], keyword, top_k=state["top_k"])

        query_params = {
            "query": keyword,
            "limit": state["top_k"],
            "alpha": HYBRID_SEARCH_ALPHA,
            "target_vector": "keywords_vector",
        }
    
        if source_name:
            query_params["filters"] = Filter.by_property("source").equal(source_name)

        try:
            response = weaviate_client.query_params(state["collection_name"], query_params)
        except Exception as e:
            logger.info("Searing with keywords failed, switching to content vector")
            query_params["target_vector"] = "content_vector"
            response = weaviate_client.query_params(state["collection_name"], query_params)

        mongo_docs = convert_mongodb_raw_docs_to_langchain_document_new(mongo_docs_raw)
        aggregated_docs_vector.extend(response)
        aggregated_docs_text.extend(mongo_docs)

    final_docs = get_top_sources(aggregated_docs_vector, top_n_source=state["top_k"], top_n_uuids=state["top_k"])
    final_mongodb_docs = sort_documents_by_score(aggregated_docs_text, state["top_k"])

    results_vector = "\n".join(doc.page_content for doc in final_docs)
    results_text = "\n".join(doc.page_content for doc in final_mongodb_docs)

    return {"messages": [{"role" : "user", "content" : [results_vector, results_text]}], "docs" : [final_docs, final_mongodb_docs]}