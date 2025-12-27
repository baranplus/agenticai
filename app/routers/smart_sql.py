from fastapi import APIRouter, HTTPException, Response, status
from langchain_core.messages import HumanMessage
import traceback

from routers import SQLDatabaseManagerDependency, SmartRAGDependency, LLMDependency

from schema.request import GeneralQueryRequest
from utils.logger import logger

router = APIRouter()

@router.post("/query")
async def query(
    sql_manager : SQLDatabaseManagerDependency,
    smart_sql_graph : SmartRAGDependency,
    llm : LLMDependency,
    request: GeneralQueryRequest
):

    try:
        init_state = {
            "messages": [HumanMessage(content=request.message)],
        }

        runtime_context = {
            "sql_manager" : sql_manager,
            "llm" : llm,
        }

        response = smart_sql_graph.invoke(init_state, context=runtime_context)

        return Response(content=response["messages"][-1].content, status_code=status.HTTP_201_CREATED)
        
    except Exception as e:
        error = traceback.format_exc()
        logger.error(f"Error processing query: {str(error)}")
        raise HTTPException(status_code=500, detail=str(e))