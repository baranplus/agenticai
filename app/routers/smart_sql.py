from fastapi import APIRouter, HTTPException, status
from langchain_core.messages import HumanMessage
import traceback

from schema.request import GeneralQueryRequest
from schema.response import GeneralResponse
from agents.graph import build_graph_smart_sql

from utils.logger import logger

router = APIRouter()

smart_sql_graph = build_graph_smart_sql()

@router.post("/query", response_model=GeneralResponse)
async def query(request: GeneralQueryRequest):

    try:
        init_state = {
            "messages": [HumanMessage(content=request.message)],
        }

        response = smart_sql_graph.invoke(init_state)

        return GeneralResponse(
            message=response["messages"][-1].content,
        )
        
    except Exception as e:
        error = traceback.format_exc()
        logger.error(f"Error processing query: {str(error)}")
        raise HTTPException(status_code=500, detail=str(e))