from fastapi import APIRouter, Depends, HTTPException
from langchain_core.messages import HumanMessage

from schema.request import QueryRequest
from schema.response import QueryResponse
from agents.graph import build_graph

from utils.logger import logger

router = APIRouter()

agentic_graph = build_graph()

@router.post("/query", response_model=QueryResponse)
async def query(request: QueryRequest):
    try:

        init_state = {"messages": [HumanMessage(content=request.message)], "rewrite_count" : 0, "docs" : [], "sourcing" : {}}

        response = agentic_graph.invoke(init_state)

        logger.info((response["messages"][-1].content))
        logger.info(len(response))
        
        return QueryResponse(
            message=response["messages"][-1].content,
        )
        
    except Exception as e:
        logger.error(f"Error processing query: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))