from pydantic import BaseModel

class AgenticRAGQueryRequest(BaseModel):
    message: str
    collection: str
    use_local_embedding : bool = True
    use_file_filtering : bool = True
    top_k: int = 5
    return_docs: bool = False
    mongodb_db : str
    mongodb_source_collection : str = "files.files"
    mongodb_pdf_pages_collection : str = "pdf_pages"
    mongodb_text_collection : str = "file_chunks"

class GeneralQueryRequest(BaseModel):
    message: str