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

    source_name = "KMC-J7.pdf"

    collection = weaviate_client.collections.get(state["collection_name"])
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

        mongo_docs_raw = mongodb_manager.full_text_search(state["mongodb_db"], state["mongodb_text_collection"], keyword, source_name, state["top_k"])
    
        try:
            response = collection.query.hybrid(
                query=keyword, 
                limit=state["top_k"], 
                alpha=HYBRID_SEARCH_ALPHA,
                target_vector="keywords_vector",
                query_properties=["content", "source", "keywords^2"],
                filters=(
                    Filter.by_property("source").equal(source_name)
                )
            )
        except Exception as e:
            logger.info("Searing with keywords failed, switching to content vector")
            response = collection.query.hybrid(
                query=keyword, 
                limit=state["top_k"], 
                alpha=HYBRID_SEARCH_ALPHA,
                target_vector="content_vector",
                filters=(
                    Filter.by_property("source").equal(source_name)
                )
            )

        docs = convert_weaviate_objects_to_langchain_docs(response.objects)
        mongo_docs = convert_mongodb_raw_docs_to_langchain_document(mongo_docs_raw)
        aggregated_docs_vector.extend(docs)
        aggregated_docs_text.extend(mongo_docs)

    final_docs = get_top_sources(aggregated_docs_vector, top_n_source=state["top_k"], top_n_uuids=state["top_k"])
    final_mongodb_docs = sort_documents_by_score(aggregated_docs_text, state["top_k"])

    results_vector = "\n".join(doc.page_content for doc in final_docs)
    results_text = "\n".join(doc.page_content for doc in final_mongodb_docs)

    return {"messages": [{"role" : "user", "content" : [results_vector, results_text]}], "docs" : [final_docs, final_mongodb_docs]}