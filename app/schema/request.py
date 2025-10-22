from pydantic import BaseModel

class QueryRequest(BaseModel):
    message: str
    collection: str
    use_local_embedding : bool = True
    top_k: int = 5