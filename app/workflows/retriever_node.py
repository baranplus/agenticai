import os
import itertools
import random
from collections import Counter
from langchain.schema import Document
from weaviate.collections.classes.internal import Object as WeaviateObject
from weaviate.classes.query import Filter
from typing import List, Iterable, Dict, Any

from .states import AgenticRAGState
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

    return remove_duplicate_documents(final_docs)

def sort_documents_by_score(docs : List[Document], top_k : int = 50) -> List[Document]:
    docs = sorted(docs, key=lambda d: d.metadata.get("score", 0), reverse=True)[:top_k]
    return remove_duplicate_documents(docs)

def remove_duplicate_documents(documents: List[Document], by: str = "uuid") -> List[Document]:
    """
    Remove duplicate documents from a list of Document objects.
    
    Args:
        documents: List of LangChain Document objects
        by: Strategy for identifying duplicates:
            - "uuid": Remove duplicates by weaviate_uuid or uuid field in metadata
            - "content": Remove duplicates by page_content (exact match)
            - "content_and_uuid": Remove duplicates by both uuid and content
            - "content_fuzzy": Remove near-duplicate content (requires similarity threshold)
    
    Returns:
        List of documents with duplicates removed, preserving order of first occurrence
        
    Example:
        >>> docs = [doc1, doc2, doc1_duplicate]  # doc1_duplicate has same UUID as doc1
        >>> unique_docs = remove_duplicate_documents(docs, by="uuid")
        >>> len(unique_docs)  # Returns 2
    """
    
    if not documents:
        return []
    
    seen = set()
    unique_docs = []
    
    if by == "uuid":
        # Remove duplicates by UUID
        for doc in documents:
            doc_uuid = doc.metadata.get('weaviate_uuid') or doc.metadata.get('uuid')
            if doc_uuid and doc_uuid not in seen:
                seen.add(doc_uuid)
                unique_docs.append(doc)
            elif not doc_uuid:
                # If no UUID, include the document (can't identify duplicate)
                unique_docs.append(doc)
    
    elif by == "content":
        # Remove duplicates by exact content match
        for doc in documents:
            content_hash = hash(doc.page_content)
            if content_hash not in seen:
                seen.add(content_hash)
                unique_docs.append(doc)
    
    elif by == "content_and_uuid":
        # Remove duplicates by both UUID and content
        for doc in documents:
            doc_uuid = doc.metadata.get('weaviate_uuid') or doc.metadata.get('uuid')
            content_hash = hash(doc.page_content)
            composite_key = (doc_uuid, content_hash)
            
            if composite_key not in seen:
                seen.add(composite_key)
                unique_docs.append(doc)
    
    elif by == "content_fuzzy":
        # Remove near-duplicates using simple similarity (content length and substring matching)
        for doc in documents:
            is_duplicate = False
            for unique_doc in unique_docs:
                # Check if documents are similar (simple heuristic)
                if doc.page_content.strip().lower() == unique_doc.page_content.strip().lower():
                    is_duplicate = True
                    break
            
            if not is_duplicate:
                unique_docs.append(doc)
    
    else:
        logger.warning(f"Unknown duplicate removal strategy: {by}. Returning original documents.")
        return documents
    
    return unique_docs

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

    unique_source = mongodb_manager.get_all_unique_filenames(state["mongodb_db"], state["mongodb_source_collection"])
    logger.info(f"Unique sources in the source collection: {unique_source}")
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
    logger.info(f"Length Mongo : {len(final_docs)}")
    logger.info(f"Length Mongo : {len(final_mongodb_docs)}")
    return {"messages": [{"role" : "user", "content" : [results_vector, results_text]}], "docs" : [final_docs, final_mongodb_docs]}