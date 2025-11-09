from fastapi import APIRouter, HTTPException, status
from fastapi.responses import Response
from langchain_core.messages import HumanMessage
import traceback

from schema.request import AgenticRAGQueryRequest
from schema.response import GeneralResponse
from agents.graph import build_graph_agentic_rag_local_embedding
from db.collection import check_collection_existence
from db import weaviate_client, mongodb_manager

from utils.logger import logger

router = APIRouter()

# agentic_graph = build_graph()
agentic_graph_local_embedding = build_graph_agentic_rag_local_embedding()


@router.post("/query")
async def query(request: AgenticRAGQueryRequest):

    if not check_collection_existence(weaviate_client, request.collection):
        
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Collection '{request.collection}' not found in the database."
        )
    
    if not mongodb_manager.check_db_existence(request.mongodb_db) or \
        not mongodb_manager.check_collection_existence(request.mongodb_db, request.mongodb_text_collection) or \
        not mongodb_manager.check_collection_existence(request.mongodb_db, request.mongodb_source_collection):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Database '{request.mongodb_db}' or Collections '{request.mongodb_source_collection}', '{request.mongodb_text_collection}' not found in the database."
        )

    try:
        init_state = {
            "messages": [HumanMessage(content=request.message)],
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

        if request.use_local_embedding:
            response = agentic_graph_local_embedding.invoke(init_state)
        else:
            return Response(content="Use local embedding for now", status_code=status.HTTP_401_UNAUTHORIZED)

        return Response(content=response["messages"][-1].content, status_code=status.HTTP_201_CREATED)
        
    except Exception as e:
        error = traceback.format_exc()
        logger.error(f"Error processing query: {str(error)}")
        raise HTTPException(status_code=500, detail=str(e))