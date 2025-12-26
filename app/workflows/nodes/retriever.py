from langgraph.runtime import Runtime
from langchain.schema import Document
from weaviate.classes.query import Filter
from typing import List

from workflows.states import AgenticRAGState, AgenticRAGContextSchema
from configs.env_configs import env_config
from utils.logger import logger

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

def retrieve_documents_by_vector_search(
    state : AgenticRAGState, 
    runtime : Runtime[AgenticRAGContextSchema]
) -> str:

    """Query vector database. Use this for any question regarding national rules of IR"""

    filenames = state["filtered_filenames"]
    query = state["messages"][-1].content
    initial_question = state["messages"][0].content
    keywords = query.split(",")
    keywords.append(initial_question)

    logger.info(f"\n\nKeywords : {keywords}\n\n")

    vector_search_docs = []

    for keyword in keywords:

        query_params = {
            "query": keyword,
            "limit": state["top_k"],
            "alpha": env_config.hybrid_search_alpha,
            "target_vector": "keywords_vector",
            "vector" : runtime.context.embedding.get_embeddings(keyword)
        }
    
        if filenames != []:
            query_params["filters"] = (Filter.by_property("filename").contains_any(filenames))

        response = runtime.context.weaviate_manager.query_params(state["weaviate_collection"], query_params)
        vector_search_docs.extend(response)

    vector_search_docs = sort_documents_by_score(vector_search_docs, state["top_k"])
    logger.info(f"Length docs vector search : {len(vector_search_docs)}")
    for doc in vector_search_docs:
        logger.info(f"Doc filename : {doc.metadata.get('filename')} - score : {doc.metadata.get('score')}")
    return { "vector_docs" : vector_search_docs }

def retrieve_documents_by_fulltext_search(
    state : AgenticRAGState, 
    runtime : Runtime[AgenticRAGContextSchema]
) -> str:

    """Query vector database. Use this for any question regarding national rules of IR"""

    filenames = state["filtered_filenames"]
    query = state["messages"][-1].content
    initial_question = state["messages"][0].content
    keywords = query.split(",")
    keywords.append(initial_question)

    logger.info(f"\n\nKeywords : {keywords}\n\n")

    fulltext_search_docs = []

    for keyword in keywords:


        response = runtime.context.mongodb_manager.full_text_search(
            state["mongodb_dbname"], 
            state["mongodb_chunk_collection"], 
            keyword,
            filenames,
            state["top_k"]
        )
        fulltext_search_docs.extend(response)
    
    fulltext_search_docs = sort_documents_by_score(fulltext_search_docs, state["top_k"])
    logger.info(f"Length docs full-text search : {len(fulltext_search_docs)}")
    for doc in fulltext_search_docs:
        logger.info(f"Doc filename : {doc.metadata.get('filename')} - score : {doc.metadata.get('score')}")
    return { "full_text_docs" : fulltext_search_docs }