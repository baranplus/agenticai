from fastapi import APIRouter, HTTPException, status
from fastapi.responses import Response
from langchain_core.messages import HumanMessage
import traceback

from schema.request import AgenticRAGQueryRequest
from agents.graph import build_graph_agentic_rag_local_embedding
from routers import (
    WeaviateClientDependency,
    MongoDBManagerDependency,
    LLMDependency,
    EmbeddingDependency
)

from utils.logger import logger

router = APIRouter()

agentic_graph_local_embedding = build_graph_agentic_rag_local_embedding()

@router.post("/query")
async def query(
    weaviate_db : WeaviateClientDependency,
    mongo_db : MongoDBManagerDependency,
    llm : LLMDependency,
    embedding : EmbeddingDependency,
    request: AgenticRAGQueryRequest
):

    if not weaviate_db.check_collection_existence(request.collection):
        
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Collection '{request.collection}' not found in the database."
        )
    
    if not mongo_db.check_db_existence(request.mongodb_db) or \
        not mongo_db.check_collection_existence(request.mongodb_db, request.mongodb_text_collection) or \
        not mongo_db.check_collection_existence(request.mongodb_db, request.mongodb_source_collection):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Database '{request.mongodb_db}' or Collections '{request.mongodb_source_collection}', '{request.mongodb_text_collection}' not found in the database."
        )

    try:
        init_state = {
            "messages": [HumanMessage(content=request.message)],
            "answers" : [],
            "rewrite_count" : 0, 
            "docs" : [],
            "sourcing" : {},
            "collection_name" : request.collection,
            "top_k" : request.top_k,
            "return_docs": request.return_docs,
            "mongodb_db" : request.mongodb_db,
            "mongodb_source_collection" : request.mongodb_source_collection,
            "mongodb_text_collection" : request.mongodb_text_collection
        }

        response = agentic_graph_local_embedding.invoke(init_state)

        return Response(content=response["messages"][-1].content, status_code=status.HTTP_201_CREATED)
        
    except Exception as e:
        error = traceback.format_exc()
        logger.error(f"Error processing query: {str(error)}")
        raise HTTPException(status_code=500, detail=str(e))