from pydantic import BaseModel

class QueryRequest(BaseModel):
    message: str
    collection: str
    use_local_embedding : bool