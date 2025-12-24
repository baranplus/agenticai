from langchain.schema import Document
from langchain_core.messages import BaseMessage
from langgraph.graph.message import add_messages
from typing import Annotated, TypedDict

class AgenticRAGState(TypedDict):
    messages: Annotated[list[BaseMessage], add_messages]
    answers: list[BaseMessage]
    docs: list[Document]
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