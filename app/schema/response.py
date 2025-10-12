from pydantic import BaseModel

class QueryResponse(BaseModel):
    message: str