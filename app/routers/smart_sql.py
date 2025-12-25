from fastapi import APIRouter, HTTPException, status
from langchain_core.messages import HumanMessage
import traceback

from schema.request import GeneralQueryRequest
from schema.response import GeneralResponse
from utils.logger import logger

router = APIRouter()

@router.post("/query")
async def query(request: GeneralQueryRequest):

    try:
        init_state = {
            "messages": [HumanMessage(content=request.message)],
        }

        return ""
        
    except Exception as e:
        error = traceback.format_exc()
        logger.error(f"Error processing query: {str(error)}")
        raise HTTPException(status_code=500, detail=str(e))