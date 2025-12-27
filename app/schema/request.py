from pydantic import BaseModel

class AgenticRAGQueryRequest(BaseModel):
    message: str
    keywords : str
    use_local_embedding : bool = True
    use_file_filtering : bool = True
    use_basic_vector_search : bool = True
    top_k: int = 5
    return_docs: bool = False
    weaviate_collection: str
    mongodb_dbname : str
    mongodb_files_collection : str = "files.files"
    mongodb_page_collection : str = "pdf_pages"
    mongodb_chunk_collection : str = "file_chunks"

class GeneralQueryRequest(BaseModel):
    message: str