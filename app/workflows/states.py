from dataclasses import dataclass
from langchain.schema import Document
from langchain_core.messages import BaseMessage
from langgraph.graph.message import add_messages
from typing import Annotated, TypedDict, List

from db import WeaviateClientManager, MongoDBManager,SQLDatabaseManager
from ai import LLM, Embedding

class AgenticRAGState(TypedDict):
    messages: Annotated[List[BaseMessage], add_messages]
    vector_docs: List[Document]
    full_text_docs: List[Document]
    sourcing_vector_search: dict
    sourcing_full_text_search : dict
    filtered_filenames : List[str]
    top_k: int
    return_docs: bool
    weaviate_collection: str
    mongodb_dbname: str
    mongodb_files_collection : str
    mongodb_page_collection : str
    mongodb_chunk_collection : str

class SmartSQLPipelineState(TypedDict):
    messages: Annotated[List[BaseMessage], add_messages]

@dataclass
class AgenticRAGContextSchema:
    weaviate_manager : WeaviateClientManager
    mongodb_manager : MongoDBManager
    llm : LLM
    embedding : Embedding
    use_file_filtering : bool

@dataclass
class SmartSQLPipelineContextSchema:
    sql_manager : SQLDatabaseManager
    llm : LLM