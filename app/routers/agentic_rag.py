from fastapi import APIRouter, HTTPException, status
from fastapi.responses import Response
from langchain_core.messages import HumanMessage, AIMessage
import traceback

from schema.request import AgenticRAGQueryRequest
from routers import (
    WeaviateClientDependency,
    MongoDBManagerDependency,
    LLMDependency,
    EmbeddingDependency,
    AgenticRagDependency
)

from utils.logger import logger

router = APIRouter()

@router.post("/query")
async def query(
    weaviate_manager : WeaviateClientDependency,
    mongodb_manager : MongoDBManagerDependency,
    llm : LLMDependency,
    embedding : EmbeddingDependency,
    agentic_graph : AgenticRagDependency,
    request: AgenticRAGQueryRequest
):

    if not weaviate_manager.check_collection_existence(request.weaviate_collection):
        
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Collection '{request.collection}' not found in the database."
        )

    if not mongodb_manager.check_db_existence(request.mongodb_dbname) or \
        not mongodb_manager.check_collection_existence(request.mongodb_dbname, request.mongodb_chunk_collection) or \
        not mongodb_manager.check_collection_existence(request.mongodb_dbname, request.mongodb_files_collection) or \
        not mongodb_manager.check_collection_existence(request.mongodb_dbname, request.mongodb_page_collection):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Database '{request.mongodb_dbname}' or Collections '{request.mongodb_files_collection}', '{request.mongodb_chunk_collection}', '{request.mongodb_page_collection}' not found in the database."
        )

    try:
        init_state = {
            "messages": [
                HumanMessage(content=request.message),
                AIMessage(content=request.keywords)
            ],
            "vector_docs" : [],
            "full_text_docs" : [],
            "sourcing_vector_search" : {},
            "sourcing_full_text_search" : {},
            "filtered_filenames" : [],
            "top_k" : request.top_k,
            "return_docs": request.return_docs,
            "weaviate_collection" : request.weaviate_collection,
            "mongodb_dbname" : request.mongodb_dbname,
            "mongodb_files_collection" : request.mongodb_files_collection,
            "mongodb_page_collection" : request.mongodb_page_collection,
            "mongodb_chunk_collection" : request.mongodb_chunk_collection
        }

        runtime_context = {
            "weaviate_manager" : weaviate_manager,
            "mongodb_manager" : mongodb_manager,
            "llm" : llm,
            "embedding" : embedding,
            "use_file_filtering" : request.use_file_filtering,
            "use_basic_vector_search" : request.use_basic_vector_search
        }

        response = agentic_graph.invoke(init_state, context=runtime_context)
        logger.info(f"Lenght Messages : {len(response["messages"])}")
        return Response(content=response["messages"][-1].content, status_code=status.HTTP_201_CREATED)
        
    except Exception as e:
        error = traceback.format_exc()
        logger.error(f"Error processing query: {str(error)}")
        raise HTTPException(status_code=500, detail=str(e))