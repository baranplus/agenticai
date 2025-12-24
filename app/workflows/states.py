from dataclasses import dataclass
from langchain.schema import Document
from langchain_core.messages import BaseMessage
from langgraph.graph.message import add_messages
from typing import Annotated, TypedDict

from db import WeaviateClientManager, MongoDBManager,SQLDatabaseManager
from ai import LLM, Embedding

class AgenticRAGState(TypedDict):
    messages: Annotated[list[BaseMessage], add_messages]
    answers: list[BaseMessage]
    vector_docs: list[Document]
    full_text_docs: list[Document]
    sourcing: dict
    rewrite_count: int
    top_k: int
    return_docs: bool
    weaviate_collection: str
    mongo_dbname: str
    mongo_files_collection : str
    mongo_page_collection : str
    mongo_chunk_collection : str

class SmartSQLPipelineState(TypedDict):
    messages: Annotated[list[BaseMessage], add_messages]

@dataclass
class AgenticRAGContextSchema:
    weaviate_manager : WeaviateClientManager
    mongodb_manager : MongoDBManager
    llm : LLM
    embedding : Embedding 

@dataclass
class SmartSQLPipelineContextSchema:
    sql_manager : SQLDatabaseManager
    llm : LLM