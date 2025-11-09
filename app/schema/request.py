from pydantic import BaseModel

class AgenticRAGQueryRequest(BaseModel):
    message: str
    collection: str
    use_local_embedding : bool = True
    top_k: int = 5
    return_docs: bool = False
    mongodb_db : str
    mongodb_source_collection : str
    mongodb_text_collection : str

class GeneralQueryRequest(BaseModel):
    message: str